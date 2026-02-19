"""
Risk Engine — Maps gene phenotypes to drug-specific risk predictions.
Uses CPIC API for authoritative data with hardcoded fallback.
Loads rules from drug_rules.json for maintainability.
"""

import json
import os
import logging
from typing import Any

from cpic_service import lookup_cpic_recommendation, fetch_gene_drug_pairs, fetch_level_a_drugs

logger = logging.getLogger(__name__)

# ── Load drug rules from JSON ──────────────────────────────────────

def _load_drug_rules() -> dict[str, Any]:
    """Load drug rules from drug_rules.json."""
    rules_path = os.path.join(os.path.dirname(__file__), "drug_rules.json")
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Remove metadata key
        data.pop("_metadata", None)
        logger.info("Loaded drug rules for %d drugs from drug_rules.json", len(data))
        return data
    except Exception as e:
        logger.warning("Failed to load drug_rules.json: %s", e)
        return {}


_DRUG_RULES = _load_drug_rules()

# CPIC uses lowercase drug names
DRUG_NAME_CPIC: dict[str, str] = {
    drug.upper(): drug.lower() for drug in _DRUG_RULES
}

# Build runtime lookup dicts from JSON data
DRUG_GENE_MAP: dict[str, str] = {
    drug: info["gene"] for drug, info in _DRUG_RULES.items()
}

RISK_MAP: dict[tuple[str, str], str] = {}
for drug, info in _DRUG_RULES.items():
    for pheno, risk in info.get("phenotype_risk", {}).items():
        RISK_MAP[(drug, pheno)] = risk

# Default severity/confidence; drug-specific overrides possible via JSON
SEVERITY_MAP: dict[str, str] = {
    "Safe": "none",
    "Adjust Dosage": "moderate",
    "Toxic": "critical",
    "Ineffective": "high",
    "Unknown": "low",
}

CONFIDENCE_MAP: dict[str, float] = {
    "Safe": 0.95,
    "Adjust Dosage": 0.85,
    "Toxic": 0.90,
    "Ineffective": 0.90,
    "Unknown": 0.30,
}

CLINICAL_RECOMMENDATIONS: dict[tuple[str, str], dict[str, Any]] = {}
for drug, info in _DRUG_RULES.items():
    for risk_label, rec in info.get("recommendations", {}).items():
        CLINICAL_RECOMMENDATIONS[(drug, risk_label)] = rec



async def assess_risk(
    drug: str,
    variants: list[dict[str, Any]],
    gene_diplotypes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Assess pharmacogenomic risk for a given drug.
    Enriches results with CPIC API data (falls back to local data).

    Args:
        drug: Drug name (uppercase)
        variants: List of parsed variant dicts
        gene_diplotypes: Dict of gene -> {diplotype, phenotype, alleles}

    Returns:
        Complete risk assessment dict with all required fields + CPIC data.
    """
    drug = drug.upper()
    primary_gene = DRUG_GENE_MAP.get(drug)

    if not primary_gene:
        # Drug not in our local rules — try CPIC guideline-only mode
        return await _cpic_guideline_result(drug, variants, gene_diplotypes)

    gene_info = gene_diplotypes.get(primary_gene)
    if not gene_info:
        return _unknown_result(drug, variants, primary_gene)

    phenotype = gene_info["phenotype"]
    diplotype = gene_info["diplotype"]

    # Look up risk from local map
    risk_label = RISK_MAP.get((drug, phenotype), "Unknown")
    severity = SEVERITY_MAP.get(risk_label, "low")
    confidence = CONFIDENCE_MAP.get(risk_label, 0.30)

    # Get local clinical recommendation (fallback)
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

    # ── CPIC API enrichment ──
    cpic_data = {
        "recommendation": None,
        "classification": None,
        "evidence_level": None,
        "guideline_name": None,
        "guideline_url": None,
        "implications": None,
        "data_source": "Local fallback",
    }

    cpic_drug_name = DRUG_NAME_CPIC.get(drug)
    if cpic_drug_name:
        try:
            cpic_rec = await lookup_cpic_recommendation(
                cpic_drug_name, primary_gene, phenotype
            )
            if cpic_rec:
                cpic_data["recommendation"] = cpic_rec.get("drugrecommendation")
                cpic_data["classification"] = cpic_rec.get("classification")
                cpic_data["guideline_name"] = cpic_rec.get("guidelinename")
                cpic_data["guideline_url"] = cpic_rec.get("guidelineurl")
                cpic_data["implications"] = cpic_rec.get("implications")
                cpic_data["data_source"] = "CPIC API"

                # Derive evidence level from gene-drug pairs
                pairs = await fetch_gene_drug_pairs(primary_gene)
                for p in pairs:
                    if p.get("drugname", "").lower() == cpic_drug_name:
                        cpic_data["evidence_level"] = p.get("cpiclevel")
                        break
        except Exception as e:
            logger.warning("CPIC enrichment failed for %s: %s", drug, e)

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
        "cpic_data": cpic_data,
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


async def _cpic_guideline_result(
    drug: str,
    variants: list[dict[str, Any]],
    gene_diplotypes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    For drugs not in our local rules, produce a professional CPIC
    guideline-based result instead of a bare 'Unknown'.
    """
    drug_lower = drug.lower()

    # Find this drug's gene from CPIC Level A data
    primary_gene = "Unknown"
    guideline_url = None
    guideline_name = None
    try:
        level_a = await fetch_level_a_drugs()
        for entry in level_a:
            if entry["drugname"] == drug_lower:
                # Take first gene (before comma if multi-gene)
                primary_gene = entry["genesymbol"].split(",")[0].strip()
                guideline_url = entry.get("guidelineurl", "")
                guideline_name = entry.get("guidelinename", "")
                break
    except Exception:
        pass

    # Try to get patient's genotype for this gene from VCF data
    gene_info = gene_diplotypes.get(primary_gene)
    diplotype = gene_info["diplotype"] if gene_info else "Not in panel"
    phenotype = gene_info["phenotype"] if gene_info else "Not determined"
    gene_variants = [v for v in variants if v.get("gene") == primary_gene]

    # Try CPIC enrichment for recommendation
    cpic_data = {
        "recommendation": None,
        "classification": None,
        "evidence_level": "A",
        "guideline_name": guideline_name,
        "guideline_url": guideline_url,
        "implications": None,
        "data_source": "CPIC API",
    }

    try:
        if gene_info and phenotype != "Unknown":
            cpic_rec = await lookup_cpic_recommendation(
                drug_lower, primary_gene, phenotype
            )
            if cpic_rec:
                cpic_data["recommendation"] = cpic_rec.get("drugrecommendation")
                cpic_data["classification"] = cpic_rec.get("classification")
                cpic_data["implications"] = cpic_rec.get("implications")
                if cpic_rec.get("guidelineurl"):
                    cpic_data["guideline_url"] = cpic_rec["guidelineurl"]
                if cpic_rec.get("guidelinename"):
                    cpic_data["guideline_name"] = cpic_rec["guidelinename"]
    except Exception as e:
        logger.warning("CPIC guideline lookup failed for %s: %s", drug, e)

    # Professional clinical recommendation
    action = f"Refer to CPIC {primary_gene} guideline for {drug.capitalize()} dosing"
    if cpic_data.get("recommendation"):
        action = cpic_data["recommendation"]

    guideline_ref = guideline_url or "https://cpicpgx.org/guidelines/"

    return {
        "risk_label": "Guideline Available",
        "confidence_score": 0.75,
        "severity": "info",
        "primary_gene": primary_gene,
        "diplotype": diplotype,
        "phenotype": phenotype,
        "detected_variants": gene_variants,
        "clinical_recommendation": {
            "action": action,
            "dosing_guidance": f"CPIC Level A guideline available for {drug.capitalize()}/{primary_gene}. Consult the published clinical guideline for genotype-specific dosing recommendations.",
            "alternative_drugs": [],
            "monitoring": "Follow CPIC guideline monitoring recommendations",
            "cpic_guideline": guideline_ref,
        },
        "cpic_data": cpic_data,
    }
