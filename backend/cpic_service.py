"""
CPIC Service — Async client for the CPIC Pharmacogenomics API.

Provides authoritative allele function, diplotype-phenotype, and drug
recommendation data from https://api.cpicpgx.org/v1/.

Features:
  - In-memory cache with 24-hour TTL
  - Graceful fallback to local data if API is unreachable
  - Async HTTP via httpx
"""

import httpx
import time
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

CPIC_BASE = "https://api.cpicpgx.org/v1"
CACHE_TTL = 86400  # 24 hours
_cache: dict[str, tuple[float, Any]] = {}

# ──────────────────────────────────────────────────────────────────────
#  Low-level helpers
# ──────────────────────────────────────────────────────────────────────

def _cache_get(key: str) -> Optional[Any]:
    """Return cached value if still fresh, else None."""
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < CACHE_TTL:
            return val
        del _cache[key]
    return None


def _cache_set(key: str, val: Any) -> None:
    _cache[key] = (time.time(), val)


async def _cpic_get(path: str, params: dict | None = None) -> list[dict]:
    """
    GET request to CPIC API. Returns parsed JSON list.
    Raises on network / HTTP errors (caller handles fallback).
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{CPIC_BASE}{path}", params=params or {})
        resp.raise_for_status()
        return resp.json()


# ──────────────────────────────────────────────────────────────────────
#  Allele function data
# ──────────────────────────────────────────────────────────────────────

async def fetch_allele_functions(gene: str) -> dict[str, dict[str, str]]:
    """
    Fetch allele → clinical function mapping from CPIC for a gene.

    Returns:
        { "*4": {"function": "No function", "activity": "0.0"}, ... }
    """
    cache_key = f"allele_func:{gene}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    data = await _cpic_get("/allele", {
        "genesymbol": f"eq.{gene}",
        "select": "name,clinicalfunctionalstatus,activityvalue",
    })

    result: dict[str, dict[str, str]] = {}
    for row in data:
        name = row.get("name", "")
        func = row.get("clinicalfunctionalstatus") or "Unknown function"
        act = row.get("activityvalue") or "n/a"
        result[name] = {"function": func, "activity": act}

    _cache_set(cache_key, result)
    return result


def cpic_function_to_internal(cpic_func: str) -> str:
    """
    Map CPIC clinical function string to our internal function key.
    CPIC uses: "Normal function", "No function", "Decreased function",
               "Increased function", "Uncertain function", "Unknown function"
    """
    mapping = {
        "Normal function": "normal_function",
        "No function": "no_function",
        "Decreased function": "decreased_function",
        "Increased function": "increased_function",
        "Uncertain function": "unknown_function",
        "Unknown function": "unknown_function",
    }
    return mapping.get(cpic_func, "unknown_function")


async def get_allele_function(gene: str, star_allele: str) -> str:
    """
    Look up allele function from CPIC.

    Args:
        gene: e.g. "CYP2D6"
        star_allele: e.g. "*4"

    Returns:
        Internal function key, e.g. "no_function"
    """
    try:
        alleles = await fetch_allele_functions(gene)
        if star_allele in alleles:
            return cpic_function_to_internal(alleles[star_allele]["function"])
    except Exception as e:
        logger.warning("CPIC allele lookup failed for %s %s: %s", gene, star_allele, e)
    return None  # caller should fall back to hardcoded


# ──────────────────────────────────────────────────────────────────────
#  Drug recommendations
# ──────────────────────────────────────────────────────────────────────

async def fetch_all_drug_recommendations(drug_name: str) -> list[dict[str, Any]]:
    """
    Fetch ALL CPIC recommendations for a drug (cached per drug).
    Returns list of recommendation dicts.
    """
    cache_key = f"all_recs:{drug_name}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = await _cpic_get("/recommendation_view", {
            "drugname": f"eq.{drug_name.lower()}",
            "select": "drugrecommendation,classification,implications,comments,"
                      "guidelinename,guidelineurl,phenotypes,lookupkey",
        })
        _cache_set(cache_key, data)
        return data
    except Exception as e:
        logger.warning("CPIC recommendation fetch failed for %s: %s", drug_name, e)
        return []


# ──────────────────────────────────────────────────────────────────────
#  Gene-drug pairs (for frontend drug picker)
# ──────────────────────────────────────────────────────────────────────

async def fetch_gene_drug_pairs(gene: str) -> list[dict[str, Any]]:
    """
    Fetch all CPIC gene-drug pairs for a gene.

    Returns list of:
        { drugname, cpiclevel, guidelinename, guidelineurl }
    """
    cache_key = f"pairs:{gene}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = await _cpic_get("/pair_view", {
            "genesymbol": f"eq.{gene}",
            "select": "drugname,cpiclevel,guidelinename,guidelineurl",
            "order": "cpiclevel.asc",
        })
        _cache_set(cache_key, data)
        return data
    except Exception as e:
        logger.warning("CPIC gene-drug pairs lookup failed for %s: %s", gene, e)
        return []


# ──────────────────────────────────────────────────────────────────────
#  Diplotype → phenotype
# ──────────────────────────────────────────────────────────────────────

async def fetch_diplotype_phenotype(
    gene: str, diplotype: str
) -> Optional[dict[str, str]]:
    """
    Fetch diplotype → phenotype from CPIC.

    Returns:
        { "generesult": "Normal Metabolizer", "totalactivityscore": "2.0" }
    """
    cache_key = f"diplo:{gene}:{diplotype}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = await _cpic_get("/diplotype", {
            "genesymbol": f"eq.{gene}",
            "diplotype": f"eq.{diplotype}",
            "select": "generesult,totalactivityscore",
        })
        if data:
            result = data[0]
            _cache_set(cache_key, result)
            return result
    except Exception as e:
        logger.warning("CPIC diplotype lookup failed for %s %s: %s",
                       gene, diplotype, e)
    return None


# ──────────────────────────────────────────────────────────────────────
#  Phenotype mapping helpers
# ──────────────────────────────────────────────────────────────────────

# CPIC phenotype text → our short code
PHENOTYPE_SHORT = {
    "Ultrarapid Metabolizer": "URM",
    "Rapid Metabolizer": "RM",
    "Normal Metabolizer": "NM",
    "Intermediate Metabolizer": "IM",
    "Poor Metabolizer": "PM",
    # SLCO1B1 uses different terms
    "Normal function": "NM",
    "Decreased function": "IM",
    "Poor function": "PM",
    "Possible Decreased function": "IM",
    "Increased function": "RM",
    # DPYD
    "Normal DPD Activity": "NM",
    "Intermediate DPD Activity": "IM",
    "Poor DPD Activity": "PM",
    # TPMT
    "Normal Activity": "NM",
    "Intermediate Activity": "IM",
    "Poor Activity": "PM",
    # Generic
    "Indeterminate": "Unknown",
}


async def lookup_cpic_recommendation(
    drug_name: str, gene: str, phenotype_short: str
) -> Optional[dict[str, Any]]:
    """
    Fetch all CPIC recommendations for a drug, then match by phenotype.

    CPIC uses inconsistent lookup keys (some drugs use activity scores,
    others use phenotype names), so we fetch all and match by the
    `phenotypes` field which always contains the human-readable phenotype.
    """
    all_recs = await fetch_all_drug_recommendations(drug_name)
    if not all_recs:
        return None

    for rec in all_recs:
        phenotypes = rec.get("phenotypes") or {}
        gene_phenotype = phenotypes.get(gene, "")
        # Map CPIC phenotype to our short code
        short_code = PHENOTYPE_SHORT.get(gene_phenotype)
        if short_code == phenotype_short:
            return rec

    return None


async def fetch_level_a_drugs() -> list[dict[str, Any]]:
    """
    Fetch all CPIC Level A gene-drug pairs.
    Returns a list of dicts: {drugname, genesymbol, guidelinename, guidelineurl, cpiclevel}
    Results are cached for 24h.
    """
    cache_key = "level_a_drugs"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        data = await _cpic_get("/pair_view", {
            "cpiclevel": "eq.A",
            "select": "drugname,genesymbol,guidelinename,guidelineurl,cpiclevel",
            "order": "drugname.asc",
        })
        # Deduplicate by drug name (keep first gene association)
        seen: dict[str, dict] = {}
        for pair in data:
            drug = pair["drugname"]
            if drug not in seen:
                seen[drug] = {
                    "drugname": drug,
                    "genesymbol": pair.get("genesymbol", ""),
                    "guidelinename": pair.get("guidelinename", ""),
                    "guidelineurl": pair.get("guidelineurl", ""),
                    "cpiclevel": pair.get("cpiclevel", "A"),
                }
            else:
                # Append additional gene if different
                existing_gene = seen[drug]["genesymbol"]
                new_gene = pair.get("genesymbol", "")
                if new_gene and new_gene not in existing_gene:
                    seen[drug]["genesymbol"] = f"{existing_gene}, {new_gene}"

        result = list(seen.values())
        _cache_set(cache_key, result)
        logger.info("Fetched %d Level A drugs from CPIC", len(result))
        return result
    except Exception as e:
        logger.warning("Failed to fetch Level A drugs: %s", e)
        return []
