"""
Risk Engine — Maps gene phenotypes to drug-specific risk predictions.
Uses hardcoded CPIC-aligned logic. Do not guess — this is the core.
"""

from typing import Any

# --- Gene-Drug Risk Mapping (CPIC-aligned) ---
# Maps (drug, phenotype) -> risk_label
RISK_MAP: dict[tuple[str, str], str] = {
    # CODEINE + CYP2D6
    ("CODEINE", "PM"): "Ineffective",
    ("CODEINE", "IM"): "Adjust Dosage",
    ("CODEINE", "NM"): "Safe",
    ("CODEINE", "RM"): "Safe",
    ("CODEINE", "URM"): "Toxic",
    # WARFARIN + CYP2C9
    ("WARFARIN", "PM"): "Adjust Dosage",
    ("WARFARIN", "IM"): "Adjust Dosage",
    ("WARFARIN", "NM"): "Safe",
    ("WARFARIN", "RM"): "Safe",
    ("WARFARIN", "URM"): "Adjust Dosage",
    # CLOPIDOGREL + CYP2C19
    ("CLOPIDOGREL", "PM"): "Ineffective",
    ("CLOPIDOGREL", "IM"): "Adjust Dosage",
    ("CLOPIDOGREL", "NM"): "Safe",
    ("CLOPIDOGREL", "RM"): "Safe",
    ("CLOPIDOGREL", "URM"): "Safe",
    # SIMVASTATIN + SLCO1B1
    ("SIMVASTATIN", "PM"): "Toxic",
    ("SIMVASTATIN", "IM"): "Adjust Dosage",
    ("SIMVASTATIN", "NM"): "Safe",
    ("SIMVASTATIN", "RM"): "Safe",
    ("SIMVASTATIN", "URM"): "Safe",
    # AZATHIOPRINE + TPMT
    ("AZATHIOPRINE", "PM"): "Toxic",
    ("AZATHIOPRINE", "IM"): "Adjust Dosage",
    ("AZATHIOPRINE", "NM"): "Safe",
    ("AZATHIOPRINE", "RM"): "Safe",
    ("AZATHIOPRINE", "URM"): "Safe",
    # FLUOROURACIL + DPYD
    ("FLUOROURACIL", "PM"): "Toxic",
    ("FLUOROURACIL", "IM"): "Adjust Dosage",
    ("FLUOROURACIL", "NM"): "Safe",
    ("FLUOROURACIL", "RM"): "Safe",
    ("FLUOROURACIL", "URM"): "Safe",
}

# Drug -> Primary Gene
DRUG_GENE_MAP: dict[str, str] = {
    "CODEINE": "CYP2D6",
    "WARFARIN": "CYP2C9",
    "CLOPIDOGREL": "CYP2C19",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD",
}

# Severity mapping
SEVERITY_MAP: dict[str, str] = {
    "Safe": "none",
    "Adjust Dosage": "moderate",
    "Toxic": "critical",
    "Ineffective": "high",
    "Unknown": "low",
}

# Confidence score mapping
CONFIDENCE_MAP: dict[str, float] = {
    "Safe": 0.95,
    "Adjust Dosage": 0.85,
    "Toxic": 0.90,
    "Ineffective": 0.90,
    "Unknown": 0.30,
}

# Clinical recommendations per (drug, risk_label)
CLINICAL_RECOMMENDATIONS: dict[tuple[str, str], dict[str, Any]] = {
    ("CODEINE", "Ineffective"): {
        "action": "Use alternative drug",
        "dosing_guidance": "Avoid codeine — patient cannot convert to morphine",
        "alternative_drugs": ["morphine", "oxycodone", "non-opioid analgesics"],
        "monitoring": "Monitor for pain relief with alternative agent",
        "cpic_guideline": "CPIC Guideline for CYP2D6 and Codeine Therapy (2019)",
    },
    ("CODEINE", "Adjust Dosage"): {
        "action": "Use with caution at reduced dose or consider alternative",
        "dosing_guidance": "Reduced codeine metabolism expected; consider 25-50% dose reduction or alternative",
        "alternative_drugs": ["morphine", "non-opioid analgesics"],
        "monitoring": "Monitor closely for lack of efficacy",
        "cpic_guideline": "CPIC Guideline for CYP2D6 and Codeine Therapy (2019)",
    },
    ("CODEINE", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing per label",
        "alternative_drugs": [],
        "monitoring": "Routine monitoring",
        "cpic_guideline": "CPIC Guideline for CYP2D6 and Codeine Therapy (2019)",
    },
    ("CODEINE", "Toxic"): {
        "action": "Avoid — life-threatening toxicity risk",
        "dosing_guidance": "Do NOT use codeine — ultrarapid conversion to morphine causes respiratory depression",
        "alternative_drugs": ["non-opioid analgesics", "acetaminophen"],
        "monitoring": "If inadvertently given, monitor for respiratory depression",
        "cpic_guideline": "CPIC Guideline for CYP2D6 and Codeine Therapy (2019)",
    },
    ("WARFARIN", "Adjust Dosage"): {
        "action": "Reduce dose",
        "dosing_guidance": "Reduce initial warfarin dose by 25-50% based on CYP2C9 status",
        "alternative_drugs": ["direct oral anticoagulants (DOACs)"],
        "monitoring": "Frequent INR monitoring, especially during initiation",
        "cpic_guideline": "CPIC Guideline for Warfarin and CYP2C9/VKORC1 (2017)",
    },
    ("WARFARIN", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing with routine INR monitoring",
        "alternative_drugs": [],
        "monitoring": "Routine INR monitoring",
        "cpic_guideline": "CPIC Guideline for Warfarin and CYP2C9/VKORC1 (2017)",
    },
    ("CLOPIDOGREL", "Ineffective"): {
        "action": "Use alternative antiplatelet",
        "dosing_guidance": "Avoid clopidogrel — patient cannot activate the prodrug",
        "alternative_drugs": ["prasugrel", "ticagrelor"],
        "monitoring": "Monitor for cardiovascular events on alternative therapy",
        "cpic_guideline": "CPIC Guideline for CYP2C19 and Clopidogrel Therapy (2022)",
    },
    ("CLOPIDOGREL", "Adjust Dosage"): {
        "action": "Consider alternative or increased dose",
        "dosing_guidance": "Reduced activation expected; consider prasugrel/ticagrelor or increased clopidogrel dose",
        "alternative_drugs": ["prasugrel", "ticagrelor"],
        "monitoring": "Monitor for cardiovascular events and platelet function",
        "cpic_guideline": "CPIC Guideline for CYP2C19 and Clopidogrel Therapy (2022)",
    },
    ("CLOPIDOGREL", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing per label",
        "alternative_drugs": [],
        "monitoring": "Routine monitoring",
        "cpic_guideline": "CPIC Guideline for CYP2C19 and Clopidogrel Therapy (2022)",
    },
    ("SIMVASTATIN", "Toxic"): {
        "action": "Use alternative statin or lower dose",
        "dosing_guidance": "Avoid simvastatin >20mg — high risk of myopathy/rhabdomyolysis",
        "alternative_drugs": ["pravastatin", "rosuvastatin"],
        "monitoring": "Monitor CK levels; report muscle pain/weakness immediately",
        "cpic_guideline": "CPIC Guideline for SLCO1B1 and Simvastatin (2014)",
    },
    ("SIMVASTATIN", "Adjust Dosage"): {
        "action": "Lower dose or use alternative",
        "dosing_guidance": "Limit simvastatin to ≤20mg daily or switch to pravastatin/rosuvastatin",
        "alternative_drugs": ["pravastatin", "rosuvastatin"],
        "monitoring": "Monitor for muscle symptoms and CK levels",
        "cpic_guideline": "CPIC Guideline for SLCO1B1 and Simvastatin (2014)",
    },
    ("SIMVASTATIN", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing per label",
        "alternative_drugs": [],
        "monitoring": "Routine lipid panel monitoring",
        "cpic_guideline": "CPIC Guideline for SLCO1B1 and Simvastatin (2014)",
    },
    ("AZATHIOPRINE", "Toxic"): {
        "action": "Drastically reduce dose or avoid",
        "dosing_guidance": "Reduce dose by 90% or avoid azathioprine — severe myelosuppression risk",
        "alternative_drugs": ["mycophenolate mofetil"],
        "monitoring": "Frequent CBC with differential; monitor for myelosuppression",
        "cpic_guideline": "CPIC Guideline for TPMT/NUDT15 and Thiopurines (2018)",
    },
    ("AZATHIOPRINE", "Adjust Dosage"): {
        "action": "Reduce initial dose",
        "dosing_guidance": "Start at 30-70% of standard dose; titrate based on tolerance",
        "alternative_drugs": ["mycophenolate mofetil"],
        "monitoring": "CBC weekly for first month, then biweekly",
        "cpic_guideline": "CPIC Guideline for TPMT/NUDT15 and Thiopurines (2018)",
    },
    ("AZATHIOPRINE", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing per label",
        "alternative_drugs": [],
        "monitoring": "Routine CBC monitoring",
        "cpic_guideline": "CPIC Guideline for TPMT/NUDT15 and Thiopurines (2018)",
    },
    ("FLUOROURACIL", "Toxic"): {
        "action": "Avoid or drastically reduce dose",
        "dosing_guidance": "Avoid 5-FU — high risk of fatal toxicity due to DPD deficiency",
        "alternative_drugs": ["non-fluoropyrimidine regimens"],
        "monitoring": "If used, monitor for severe mucositis, myelosuppression, neurotoxicity",
        "cpic_guideline": "CPIC Guideline for DPYD and Fluoropyrimidines (2017)",
    },
    ("FLUOROURACIL", "Adjust Dosage"): {
        "action": "Reduce initial dose",
        "dosing_guidance": "Start at 25-50% of standard dose; titrate based on tolerance",
        "alternative_drugs": ["non-fluoropyrimidine regimens"],
        "monitoring": "Close monitoring for mucositis, myelosuppression",
        "cpic_guideline": "CPIC Guideline for DPYD and Fluoropyrimidines (2017)",
    },
    ("FLUOROURACIL", "Safe"): {
        "action": "Use as directed",
        "dosing_guidance": "Standard dosing per label",
        "alternative_drugs": [],
        "monitoring": "Routine monitoring for fluoropyrimidine toxicity",
        "cpic_guideline": "CPIC Guideline for DPYD and Fluoropyrimidines (2017)",
    },
}


def assess_risk(
    drug: str,
    variants: list[dict[str, Any]],
    gene_diplotypes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Assess pharmacogenomic risk for a given drug.

    Args:
        drug: Drug name (uppercase)
        variants: List of parsed variant dicts
        gene_diplotypes: Dict of gene -> {diplotype, phenotype, alleles}

    Returns:
        Complete risk assessment dict with all required fields.
    """
    drug = drug.upper()
    primary_gene = DRUG_GENE_MAP.get(drug)

    if not primary_gene:
        # Unsupported drug
        return _unknown_result(drug, variants)

    gene_info = gene_diplotypes.get(primary_gene)
    if not gene_info:
        return _unknown_result(drug, variants, primary_gene)

    phenotype = gene_info["phenotype"]
    diplotype = gene_info["diplotype"]

    # Look up risk
    risk_label = RISK_MAP.get((drug, phenotype), "Unknown")
    severity = SEVERITY_MAP.get(risk_label, "low")
    confidence = CONFIDENCE_MAP.get(risk_label, 0.30)

    # Get clinical recommendation
    rec = CLINICAL_RECOMMENDATIONS.get(
        (drug, risk_label),
        {
            "action": "Consult clinical pharmacogenomics specialist",
            "dosing_guidance": "Insufficient data for automated recommendation",
            "alternative_drugs": [],
            "monitoring": "Standard monitoring",
            "cpic_guideline": "N/A",
        },
    )

    # Filter variants for this gene
    gene_variants = [v for v in variants if v.get("gene") == primary_gene]

    return {
        "risk_label": risk_label,
        "confidence_score": confidence,
        "severity": severity,
        "primary_gene": primary_gene,
        "diplotype": diplotype,
        "phenotype": phenotype,
        "detected_variants": gene_variants,
        "clinical_recommendation": rec,
    }


def _unknown_result(
    drug: str,
    variants: list[dict[str, Any]],
    primary_gene: str = "Unknown",
) -> dict[str, Any]:
    """Return an Unknown result for unsupported drugs or missing gene data."""
    return {
        "risk_label": "Unknown",
        "confidence_score": 0.30,
        "severity": "low",
        "primary_gene": primary_gene,
        "diplotype": "Unknown",
        "phenotype": "Unknown",
        "detected_variants": [],
        "clinical_recommendation": {
            "action": "Consult clinical pharmacogenomics specialist",
            "dosing_guidance": "No pharmacogenomic data available for this drug-gene pair",
            "alternative_drugs": [],
            "monitoring": "Standard monitoring",
            "cpic_guideline": "N/A",
        },
    }
