"""
VCF Parser — Parses VCF files and extracts pharmacogenomic variants.

Design Guidelines:
  - Only INFO (col 7) and ID (col 2) columns matter
  - REF, ALT, QUAL, FILTER are completely ignored
  - Lines are skipped, never rejected mid-way
  - Only rejection: zero valid PGx variants after processing all lines
  - All INFO keys and values are uppercased for case-insensitive matching
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
    ("CYP2D6", "*1XN"): "increased_function",
    ("CYP2D6", "*2XN"): "increased_function",
    # CYP2C19
    ("CYP2C19", "*1"): "normal_function",
    ("CYP2C19", "*2"): "no_function",
    ("CYP2C19", "*3"): "no_function",
    ("CYP2C19", "*17"): "increased_function",
    # CYP2C9
    ("CYP2C9", "*1"): "normal_function",
    ("CYP2C9", "*2"): "decreased_function",
    ("CYP2C9", "*3"): "no_function",
    ("CYP2C9", "*6"): "no_function",
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
    """
    Parse VCF INFO field into a dict.
    Rule 4: Split by ";", then "=". Strip whitespace.
    Convert ALL keys AND values to UPPERCASE.
    Ignore tags without "=".
    """
    info = {}
    for item in info_str.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            info[key.strip().upper()] = value.strip().upper()
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

    if funcs == ["no_function", "no_function"]:
        return "PM"
    if funcs == ["decreased_function", "no_function"]:
        return "PM"
    if funcs == ["decreased_function", "decreased_function"]:
        return "IM"
    if "no_function" in funcs and "normal_function" in funcs:
        return "IM"
    if "decreased_function" in funcs and "normal_function" in funcs:
        return "IM"
    if funcs == ["normal_function", "normal_function"]:
        return "NM"
    if "increased_function" in funcs and "normal_function" in funcs:
        return "RM"
    if funcs == ["increased_function", "increased_function"]:
        return "URM"
    if "increased_function" in funcs and "no_function" in funcs:
        return "IM"
    if "increased_function" in funcs and "decreased_function" in funcs:
        return "NM"

    return "Unknown"


def parse_vcf(vcf_text: str) -> dict[str, Any]:
    """
    Parse a VCF file and extract pharmacogenomic variants.

    Design:
      - Lines starting with ## or # are skipped
      - Empty / whitespace-only lines are skipped
      - Lines split by TAB only; <8 columns → skip
      - Only INFO (col 7) and ID (col 2) are used
      - REF, ALT, QUAL, FILTER are ignored completely
      - INFO keys + values uppercased for case-insensitive matching
      - Never rejects mid-way — only lines are skipped
      - Final check: if zero variants extracted → raise ValueError

    Raises:
        ValueError: Only if zero pharmacogenomic variants found.

    Returns:
        { "patient_id": str, "variants": [...], "gene_diplotypes": {...} }
    """
    lines = vcf_text.strip().split("\n")

    # ── Extract patient ID from #CHROM header (if FORMAT + sample cols exist) ──
    patient_id = "PATIENT_UNKNOWN"
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#CHROM"):
            header_cols = stripped.split("\t")
            # Look for FORMAT column → sample name is the column after it
            for idx, col in enumerate(header_cols):
                if col == "FORMAT" and idx + 1 < len(header_cols):
                    patient_id = header_cols[idx + 1]
                    break
            break

    # ── Process every line ──
    variants: list[dict[str, Any]] = []
    gene_star_alleles: dict[str, list[str]] = {g: [] for g in PHARMACO_GENES}
    gene_variant_count: dict[str, int] = {}

    for line in lines:
        stripped = line.strip()

        # Rule 2: Skip meta-lines, header lines, and empty lines
        if not stripped or stripped.startswith("#"):
            continue

        # Rule 2: Split by TAB only — never by space
        cols = stripped.split("\t")

        # Rule 2: Skip lines with fewer than 8 columns
        if len(cols) < 8:
            continue

        # Rule 3: RSID = columns[2], INFO = columns[7]
        rsid_col = cols[2]
        info_str = cols[7]

        # Rule 4: If INFO is "." or empty → skip this line
        if info_str.strip() in (".", ""):
            continue

        # Rule 4: Parse INFO — split by ";", then "=", uppercase keys+values
        info = _parse_info_field(info_str)

        # Rule 5: Extract GENE, STAR, RS
        gene = info.get("GENE", "")
        star_allele = info.get("STAR", "")
        rs_from_info = info.get("RS", "")

        # Rule 5: GENE not found or empty → skip this line
        if not gene:
            continue

        # Rule 5: STAR not found or empty → mark as "UNKNOWN", do NOT skip
        if not star_allele:
            star_allele = "UNKNOWN"

        # Rule 5: RS not found → use ID column; if ID is also "." → use "."
        if rs_from_info:
            rsid = rs_from_info
        elif rsid_col and rsid_col != ".":
            rsid = rsid_col
        else:
            rsid = "."

        # Gene must be a recognized pharmacogene → skip if not
        if gene not in PHARMACO_GENES:
            continue

        # Rule 6: Max 2 variants per gene — first 2 by appearance order
        gene_variant_count[gene] = gene_variant_count.get(gene, 0) + 1
        if gene_variant_count[gene] > 2:
            continue

        # ── Build variant entry ──
        # Extract genotype from FORMAT + sample columns (if available)
        genotype = "."
        if len(cols) >= 10:
            fmt = cols[8].split(":")
            sample = cols[9].split(":")
            if "GT" in fmt:
                gt_idx = fmt.index("GT")
                if gt_idx < len(sample):
                    genotype = sample[gt_idx]

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
            clin_sig = "drug_response"

        variant_entry = {
            "rsid": rsid,
            "gene": gene,
            "chromosome": cols[0],
            "position": int(cols[1]),
            "ref_allele": cols[3] if len(cols) > 3 else ".",
            "alt_allele": cols[4] if len(cols) > 4 else ".",
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

    # ── Rule 7: Final check — reject only if zero variants ──
    if len(variants) == 0:
        raise ValueError(
            "No valid pharmacogenomic variants found in this VCF file"
        )

    # ── Build diplotypes per gene ──
    gene_diplotypes: dict[str, dict[str, str]] = {}
    for gene in PHARMACO_GENES:
        detected = gene_star_alleles[gene]

        if len(detected) == 0:
            diplotype = "*1/*1"
            phenotype = "NM"
            alleles = ["*1", "*1"]
        elif len(detected) == 1:
            alleles = sorted(["*1", detected[0]])
            diplotype = f"{alleles[0]}/{alleles[1]}"
            func1 = _get_function(gene, alleles[0])
            func2 = _get_function(gene, alleles[1])
            phenotype = _diplotype_to_phenotype(gene, func1, func2)
        else:
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
