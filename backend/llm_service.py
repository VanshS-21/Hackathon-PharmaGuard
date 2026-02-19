"""
LLM Service — Generates clinical explanations using Google Gemini API.
"""

import json
import logging
import os
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

# System instruction for clinical explanations
SYSTEM_INSTRUCTION = """You are a clinical pharmacogenomics expert assistant. 
Given a patient's genetic variant data and drug risk assessment, generate a clear, 
concise clinical explanation that:
1. Summarizes the key finding in 2-3 sentences (summary)
2. Explains the biological mechanism of how the gene variant affects drug metabolism (mechanism)
3. States the evidence level based on CPIC guidelines (evidence_level)
4. Cites relevant CPIC guidelines or literature (references)

Output ONLY valid JSON with these exact keys: summary, mechanism, evidence_level, references.
Do NOT include markdown formatting, code blocks, or any other text outside the JSON.
The "references" field should be a JSON array of strings."""


async def generate_explanation(
    drug: str,
    risk_result: dict[str, Any],
    variants: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate an LLM clinical explanation for a drug risk assessment.

    Args:
        drug: Drug name
        risk_result: Output from risk engine
        variants: All parsed variants

    Returns:
        Dict with keys: summary, mechanism, evidence_level, references
    """
    # Build prompt
    gene = risk_result.get("primary_gene", "Unknown")
    diplotype = risk_result.get("diplotype", "Unknown")
    phenotype = risk_result.get("phenotype", "Unknown")
    risk_label = risk_result.get("risk_label", "Unknown")
    severity = risk_result.get("severity", "Unknown")

    _ALT_GENOTYPES = {"0/1", "0|1", "1/0", "1|0", "1/1", "1|1"}
    gene_variants = [
        v for v in variants
        if v.get("gene") == gene and v.get("genotype") in _ALT_GENOTYPES
    ]
    variant_details = ""
    for v in gene_variants:
        variant_details += (
            f"  - {v['rsid']}: {v['gene']} {v['star_allele']} "
            f"(genotype: {v['genotype']}, {v['clinical_significance']})\n"
        )

    if not variant_details:
        variant_details = "  No pharmacogenomic variants detected for this gene.\n"

    prompt = f"""Analyze the following pharmacogenomic finding and generate a clinical explanation.

Patient Pharmacogenomic Profile:
- Drug: {drug}
- Primary Gene: {gene}
- Diplotype: {diplotype}
- Phenotype: {phenotype}
- Risk Label: {risk_label}
- Severity: {severity}

Detected Variants:
{variant_details}

Clinical Recommendation: {risk_result.get('clinical_recommendation', {}).get('dosing_guidance', 'N/A')}

Generate a JSON response with: summary, mechanism, evidence_level, references."""

    try:
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=SYSTEM_INSTRUCTION,
        )
        response = await model.generate_content_async(prompt)

        # Parse the response text as JSON
        text = response.text.strip()
        # Remove potential markdown code block wrapping
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()
        if text.startswith("json"):
            text = text[4:].strip()

        explanation = json.loads(text)

        # Ensure all required keys exist
        return {
            "summary": explanation.get("summary", ""),
            "mechanism": explanation.get("mechanism", ""),
            "evidence_level": explanation.get("evidence_level", ""),
            "references": explanation.get("references", []),
        }

    except Exception as e:
        logger.warning("LLM explanation failed for %s: %s", drug, e)
        return _fallback_explanation(drug, risk_result, gene_variants)


def _fallback_explanation(
    drug: str,
    risk_result: dict[str, Any],
    gene_variants: list[dict[str, Any]],
) -> dict[str, Any]:
    """Generate a deterministic fallback explanation when LLM fails."""
    gene = risk_result.get("primary_gene", "Unknown")
    diplotype = risk_result.get("diplotype", "Unknown")
    phenotype = risk_result.get("phenotype", "Unknown")
    risk_label = risk_result.get("risk_label", "Unknown")

    phenotype_full = {
        "PM": "Poor Metabolizer",
        "IM": "Intermediate Metabolizer",
        "NM": "Normal Metabolizer",
        "RM": "Rapid Metabolizer",
        "URM": "Ultrarapid Metabolizer",
    }.get(phenotype, phenotype)

    MECHANISM_MAP = {
        "CYP2D6": f"CYP2D6 enzyme metabolizes codeine to its active form morphine. The {diplotype} diplotype results in {phenotype_full} status, affecting morphine production.",
        "CYP2C19": f"CYP2C19 enzyme activates the prodrug clopidogrel. The {diplotype} diplotype results in {phenotype_full} status, affecting drug activation.",
        "CYP2C9": f"CYP2C9 enzyme metabolizes warfarin. The {diplotype} diplotype results in {phenotype_full} status, affecting drug clearance and bleeding risk.",
        "SLCO1B1": f"SLCO1B1 transporter mediates hepatic uptake of simvastatin. The {diplotype} diplotype results in {phenotype_full} status, affecting drug clearance and myopathy risk.",
        "TPMT": f"TPMT enzyme metabolizes thiopurine drugs. The {diplotype} diplotype results in {phenotype_full} status, affecting myelosuppression risk.",
        "DPYD": f"DPYD enzyme is the rate-limiting step in fluoropyrimidine catabolism. The {diplotype} diplotype results in {phenotype_full} status, affecting toxicity risk.",
    }

    rsids = ", ".join(v["rsid"] for v in gene_variants) if gene_variants else "none detected"

    return {
        "summary": (
            f"Patient carries a {gene} {diplotype} diplotype, classified as {phenotype_full}. "
            f"For {drug}, this results in a '{risk_label}' risk assessment. "
            f"Detected variant(s): {rsids}."
        ),
        "mechanism": MECHANISM_MAP.get(gene, f"{gene} affects the metabolism of {drug}."),
        "evidence_level": "1A — strong evidence, CPIC Level A recommendation",
        "references": [
            f"CPIC Guideline for {gene} and {drug} Therapy",
            "PharmGKB (https://www.pharmgkb.org)",
        ],
    }
