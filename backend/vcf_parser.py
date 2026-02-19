"""
VCF Parser — Parses VCF v4.2 files and extracts pharmacogenomic variants.
Extracts variants for genes: CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
"""

from typing import Any

# Genes we care about
PHARMACO_GENES = {"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"}

# Star allele function mapping (simplified for MVP)
# Maps (gene, star_allele) -> function
STAR_ALLELE_FUNCTION: dict[tuple[str, str], str] = {
    # CYP2D6
    ("CYP2D6", "*1"): "normal_function",
    ("CYP2D6", "*2"): "normal_function",
    ("CYP2D6", "*3"): "no_function",
    ("CYP2D6", "*4"): "no_function",
    ("CYP2D6", "*5"): "no_function",
    ("CYP2D6", "*6"): "no_function",
    ("CYP2D6", "*9"): "decreased_function",
    ("CYP2D6", "*10"): "decreased_function",
    ("CYP2D6", "*17"): "decreased_function",
    ("CYP2D6", "*41"): "decreased_function",
    ("CYP2D6", "*1xN"): "increased_function",
    ("CYP2D6", "*2xN"): "increased_function",
    # CYP2C19
    ("CYP2C19", "*1"): "normal_function",
    ("CYP2C19", "*2"): "no_function",
    ("CYP2C19", "*3"): "no_function",
    ("CYP2C19", "*17"): "increased_function",
    # CYP2C9
    ("CYP2C9", "*1"): "normal_function",
    ("CYP2C9", "*2"): "decreased_function",
    ("CYP2C9", "*3"): "no_function",
    # SLCO1B1
    ("SLCO1B1", "*1"): "normal_function",
    ("SLCO1B1", "*5"): "decreased_function",
    ("SLCO1B1", "*15"): "decreased_function",
    ("SLCO1B1", "*17"): "decreased_function",
    # TPMT
    ("TPMT", "*1"): "normal_function",
    ("TPMT", "*2"): "no_function",
    ("TPMT", "*3A"): "no_function",
    ("TPMT", "*3B"): "no_function",
    ("TPMT", "*3C"): "no_function",
    # DPYD
    ("DPYD", "*1"): "normal_function",
    ("DPYD", "*2A"): "no_function",
    ("DPYD", "*13"): "no_function",
}


def _parse_info_field(info_str: str) -> dict[str, str]:
    """Parse VCF INFO field: GENE=CYP2D6;STAR=*4;RS=rs3892097 -> dict"""
    info = {}
    for item in info_str.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            info[key.strip().upper()] = value.strip()
    return info


def _get_function(gene: str, star_allele: str) -> str:
    """Look up function for a gene/star allele combo."""
    return STAR_ALLELE_FUNCTION.get((gene, star_allele), "unknown_function")


def _diplotype_to_phenotype(gene: str, allele1_func: str, allele2_func: str) -> str:
    """
    Determine phenotype from two allele functions.
    Uses simplified CPIC activity scoring rules.
    """
    funcs = sorted([allele1_func, allele2_func])

    # Both no function -> Poor Metabolizer
    if funcs == ["no_function", "no_function"]:
        return "PM"
    # One no function + one decreased
    if funcs == ["decreased_function", "no_function"]:
        return "PM"
    # Both decreased
    if funcs == ["decreased_function", "decreased_function"]:
        return "IM"
    # One normal + one no function OR one normal + one decreased
    if "no_function" in funcs and "normal_function" in funcs:
        return "IM"
    if "decreased_function" in funcs and "normal_function" in funcs:
        return "IM"
    # Both normal
    if funcs == ["normal_function", "normal_function"]:
        return "NM"
    # One increased + one normal
    if "increased_function" in funcs and "normal_function" in funcs:
        return "RM"
    # Both increased, or one increased + one no/decreased
    if funcs == ["increased_function", "increased_function"]:
        return "URM"
    if "increased_function" in funcs and "no_function" in funcs:
        return "IM"
    if "increased_function" in funcs and "decreased_function" in funcs:
        return "NM"

    return "Unknown"


def parse_vcf(vcf_text: str) -> dict[str, Any]:
    """
    Parse a VCF file text and extract pharmacogenomic variants.
    Performs structural validation before parsing.

    Raises:
        ValueError: If the VCF file fails any validation check.

    Returns:
        {
            "patient_id": str,
            "variants": [...],
            "gene_diplotypes": {...}
        }
    """
    lines = vcf_text.strip().split("\n")

    # ── CHECK 4: Validate ##fileformat=VCFv4.2 header ──
    if not lines or not lines[0].strip().startswith("##fileformat=VCFv4.2"):
        raise ValueError("Not a valid VCF v4.2 file")

    # ── CHECK 5: Validate #CHROM header line exists ──
    chrom_header_line = None
    chrom_header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("#CHROM"):
            chrom_header_line = line.strip()
            chrom_header_idx = i
            break
    if chrom_header_line is None:
        raise ValueError("Invalid VCF structure. Missing column header")

    # ── CHECK 6: Dynamically detect INFO column position ──
    header_cols = chrom_header_line.split("\t")
    info_col_idx = None
    for idx, col in enumerate(header_cols):
        if col.upper() == "INFO":
            info_col_idx = idx
            break
    if info_col_idx is None:
        raise ValueError("INFO column not found in header")

    # Extract patient ID from header (first sample column, after FORMAT)
    patient_id = "PATIENT_UNKNOWN"
    format_col_idx = None
    for idx, col in enumerate(header_cols):
        if col.upper() == "FORMAT":
            format_col_idx = idx
            break
    if format_col_idx is not None and len(header_cols) > format_col_idx + 1:
        patient_id = header_cols[format_col_idx + 1]

    # ── Collect data rows (lines after #CHROM that don't start with #) ──
    data_lines = []
    for line in lines[chrom_header_idx + 1:]:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            data_lines.append(stripped)

    # ── CHECK 8: At least 1 valid data row ──
    if len(data_lines) == 0:
        raise ValueError("VCF file has no valid data rows")

    # ── CHECK 7: At least one row has GENE= and STAR= tags ──
    has_pgx_annotations = False
    for dl in data_lines:
        cols = dl.split("\t")
        if len(cols) > info_col_idx:
            info_field = cols[info_col_idx]
            if "GENE=" in info_field and "STAR=" in info_field:
                has_pgx_annotations = True
                break
    if not has_pgx_annotations:
        raise ValueError("VCF file missing pharmacogenomic annotations")

    # ── Parse validated data rows ──
    variants: list[dict[str, Any]] = []
    gene_star_alleles: dict[str, list[str]] = {g: [] for g in PHARMACO_GENES}

    for dl in data_lines:
        cols = dl.split("\t")
        if len(cols) <= info_col_idx:
            continue

        chrom = cols[0]
        pos = cols[1]
        rsid_col = cols[2] if len(cols) > 2 else "."
        ref = cols[3] if len(cols) > 3 else "."
        alt = cols[4] if len(cols) > 4 else "."
        info_str = cols[info_col_idx]

        # Parse INFO
        info = _parse_info_field(info_str)
        gene = info.get("GENE", "").strip().upper()  # Step 11+12: strip & uppercase
        star_allele = info.get("STAR", "").strip().upper()  # Step 11+12
        rsid = info.get("RS", rsid_col if rsid_col != "." else "").strip()
        clnsig = info.get("CLNSIG", "drug_response").strip()

        # Skip if GENE tag missing
        if not gene:
            continue

        # Skip if not a pharmacogenomic gene
        if gene not in PHARMACO_GENES:
            continue

        # Step 13: Max 2 variants per gene (diplotype = 2 alleles)
        gene_variant_count = sum(1 for v in variants if v["gene"] == gene)
        if gene_variant_count >= 2:
            continue

        # Extract genotype from FORMAT + sample columns
        genotype = "."
        if format_col_idx is not None and len(cols) > format_col_idx + 1:
            fmt = cols[format_col_idx].split(":")
            sample = cols[format_col_idx + 1].split(":")
            if "GT" in fmt:
                gt_idx = fmt.index("GT")
                if gt_idx < len(sample):
                    genotype = sample[gt_idx]

        # Determine if variant is present (alt allele detected)
        is_het = genotype in ("0/1", "0|1", "1/0", "1|0")
        is_hom_alt = genotype in ("1/1", "1|1")

        # Map star allele function
        allele_function = _get_function(gene, star_allele)

        # Determine clinical significance description
        if allele_function == "no_function":
            clin_sig = "Loss of function"
        elif allele_function == "decreased_function":
            clin_sig = "Decreased function"
        elif allele_function == "increased_function":
            clin_sig = "Increased function"
        elif allele_function == "normal_function":
            clin_sig = "Normal function"
        else:
            clin_sig = clnsig

        variant_entry = {
            "rsid": rsid,
            "gene": gene,
            "chromosome": chrom,
            "position": int(pos),
            "ref_allele": ref,
            "alt_allele": alt,
            "genotype": genotype,
            "star_allele": star_allele,
            "clinical_significance": clin_sig,
        }
        variants.append(variant_entry)

        # Track star alleles for diplotype calling
        if is_hom_alt and star_allele:
            gene_star_alleles[gene].append(star_allele)
            gene_star_alleles[gene].append(star_allele)
        elif is_het and star_allele:
            gene_star_alleles[gene].append(star_allele)

    # --- Build diplotypes per gene ---
    gene_diplotypes: dict[str, dict[str, str]] = {}
    for gene in PHARMACO_GENES:
        detected = gene_star_alleles[gene]

        if len(detected) == 0:
            # No variants detected -> assume *1/*1 (wild-type / normal)
            diplotype = "*1/*1"
            phenotype = "NM"
            alleles = ["*1", "*1"]
        elif len(detected) == 1:
            # One variant allele + one wild-type *1
            alleles = sorted(["*1", detected[0]])
            diplotype = f"{alleles[0]}/{alleles[1]}"
            func1 = _get_function(gene, alleles[0])
            func2 = _get_function(gene, alleles[1])
            phenotype = _diplotype_to_phenotype(gene, func1, func2)
        else:
            # Two or more variant alleles — take first two
            alleles = sorted(detected[:2])
            diplotype = f"{alleles[0]}/{alleles[1]}"
            func1 = _get_function(gene, alleles[0])
            func2 = _get_function(gene, alleles[1])
            phenotype = _diplotype_to_phenotype(gene, func1, func2)

        gene_diplotypes[gene] = {
            "diplotype": diplotype,
            "phenotype": phenotype,
            "alleles": alleles,
        }

    return {
        "patient_id": patient_id,
        "variants": variants,
        "gene_diplotypes": gene_diplotypes,
    }
