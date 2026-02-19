"""
PharmaGuard — FastAPI Backend
Pharmacogenomic Risk Prediction System

Best practices applied:
  - Pydantic response models for type safety & auto-documented API schema
  - Global exception handler to prevent stack-trace leaks
  - Restrictive CORS (only GET/POST/OPTIONS, explicit headers)
  - Rate limiting on the expensive /api/analyze endpoint (slowapi)
  - Guard clauses & early returns for all validation
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from datetime import datetime, timezone
from typing import Any

from vcf_parser import parse_vcf
from risk_engine import assess_risk
from llm_service import generate_explanation
from cpic_service import fetch_gene_drug_pairs, fetch_level_a_drugs

load_dotenv()
logger = logging.getLogger(__name__)

# ── Rate limiter ────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# Our fully-supported drugs (have VCF analysis rules)
SUPPORTED_DRUGS = {"codeine", "warfarin", "clopidogrel", "simvastatin", "azathioprine", "fluorouracil"}


# ── Pydantic Response Models ───────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(example="healthy")
    timestamp: str = Field(example="2026-02-19T16:00:00+00:00")


class RootResponse(BaseModel):
    status: str = Field(example="ok")
    service: str = Field(example="PharmaGuard API")
    version: str = Field(example="1.0.0")


class CpicDrugItem(BaseModel):
    drugname: str
    genesymbol: str | None = None
    guidelinename: str | None = None
    guidelineurl: str | None = None
    cpiclevel: str | None = None
    supported: bool


class CpicLevelAResponse(BaseModel):
    drugs: list[CpicDrugItem]
    total: int


class GeneDrugPair(BaseModel):
    drugname: str | None = None
    genesymbol: str | None = None
    guidelinename: str | None = None
    guidelineurl: str | None = None
    cpiclevel: str | None = None


class GeneDrugResponse(BaseModel):
    gene: str
    drugs: list[GeneDrugPair]


# Response type for /api/analyze — bare list per the problem statement schema
AnalyzeResponse = list[dict[str, Any]]


# ── FastAPI App ─────────────────────────────────────────────────────

app = FastAPI(
    title="PharmaGuard API",
    description="Pharmacogenomic Risk Prediction System — RIFT 2026 Hackathon",
    version="1.0.0",
)

# Attach rate limiter
app.state.limiter = limiter


# ── Global Exception Handlers ──────────────────────────────────────

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Return a clean 429 instead of exposing rate-limit internals."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all: never leak stack traces to the client."""
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )


# ── Middleware ──────────────────────────────────────────────────────

# CORS — restrictive methods but permissive headers (browser preflight)
# NOTE: Added AFTER TrustedHost so CORS runs FIRST (FastAPI middleware is LIFO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted hosts (localhost for dev, add production domain later)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*"],
)


# ── Routes ──────────────────────────────────────────────────────────

@app.get("/", response_model=RootResponse)
def root():
    return {"status": "ok", "service": "PharmaGuard API", "version": "1.0.0"}


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/cpic/level-a-drugs", response_model=CpicLevelAResponse)
async def level_a_drugs():
    """
    GET /api/cpic/level-a-drugs
    Returns all CPIC Level A gene-drug pairs, marking which ones
    have full VCF analysis support in PharmaGuard.
    """
    drugs = await fetch_level_a_drugs()
    enriched = [
        {**d, "supported": d["drugname"] in SUPPORTED_DRUGS}
        for d in drugs
    ]
    return {"drugs": enriched, "total": len(enriched)}


@app.get("/api/cpic/drugs/{gene}", response_model=GeneDrugResponse)
async def cpic_drugs(gene: str):
    """
    GET /api/cpic/drugs/{gene}
    Returns all CPIC gene-drug pairs for a given gene symbol.
    """
    gene = gene.upper()
    pairs = await fetch_gene_drug_pairs(gene)
    return {"gene": gene, "drugs": pairs}


@app.post("/api/analyze", response_model=list[dict[str, Any]])
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    vcf_file: UploadFile = File(..., description="VCF file (.vcf, max 5 MB)"),
    drugs: str = Form(..., description="Comma-separated drug names, e.g. CODEINE,WARFARIN"),
):
    """
    POST /api/analyze
    Input: VCF file (multipart) + drugs (form field, comma-separated)
    Output: List of risk assessment JSON objects per drug
    """
    # --- Validate file ---
    if not vcf_file.filename or not vcf_file.filename.lower().endswith(".vcf"):
        raise HTTPException(status_code=400, detail="Invalid file format. Only .vcf files accepted")

    contents = await vcf_file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5 MB")

    try:
        vcf_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8")

    # --- Validate drugs input ---
    drug_list = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    if not drug_list:
        raise HTTPException(status_code=400, detail="At least one drug name is required")
    if len(drug_list) > 20:
        raise HTTPException(status_code=400, detail="Too many drugs. Maximum 20 per request")

    # Sanitize: only alphanumeric + hyphen allowed in drug names
    for d in drug_list:
        if not all(c.isalnum() or c == "-" for c in d):
            raise HTTPException(status_code=400, detail=f"Invalid drug name: {d}")

    # --- Parse VCF ---
    try:
        parsed = parse_vcf(vcf_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.warning("VCF parsing error: %s", e)
        raise HTTPException(status_code=422, detail="VCF parsing error. Please check your file format")

    # --- Process each drug ---
    patient_id = parsed["patient_id"]  # Read from VCF sample column, not randomly generated
    timestamp = datetime.now(timezone.utc).isoformat()

    results = []
    for drug in drug_list:
        # Risk assessment (async — includes CPIC enrichment)
        risk_result = await assess_risk(drug, parsed["variants"], parsed["gene_diplotypes"])

        # LLM explanation
        explanation = await generate_explanation(
            drug=drug,
            risk_result=risk_result,
            variants=parsed["variants"],
        )

        # Only count variants where the patient actually carries the alt allele
        _ALT_GENOTYPES = {"0/1", "0|1", "1/0", "1|0", "1/1", "1|1"}
        alt_variant_count = len(
            [v for v in parsed["variants"] if v.get("genotype") in _ALT_GENOTYPES]
        )
        # Fixed ordered gene list — deterministic, covers all 6 pharmacogenes
        GENE_ORDER = ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]
        gene_coverage = [g for g in GENE_ORDER if g in parsed["gene_diplotypes"]]

        result = {
            "patient_id": patient_id,
            "drug": drug,
            "timestamp": timestamp,
            "risk_assessment": {
                "risk_label": risk_result["risk_label"],
                "confidence_score": risk_result["confidence_score"],
                "severity": risk_result["severity"],
            },
            "pharmacogenomic_profile": {
                "primary_gene": risk_result["primary_gene"],
                "diplotype": risk_result["diplotype"],
                "phenotype": risk_result["phenotype"],
                "detected_variants": risk_result["detected_variants"],
            },
            "clinical_recommendation": risk_result["clinical_recommendation"],
            "llm_generated_explanation": explanation,
            "quality_metrics": {
                "vcf_parsing_success": True,
                "variants_detected_count": alt_variant_count,
                "gene_coverage": gene_coverage,
                "analysis_timestamp": timestamp,
            },
        }
        results.append(result)

    return results
