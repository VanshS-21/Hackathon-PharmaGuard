"""
PharmaGuard — FastAPI Backend
Pharmacogenomic Risk Prediction System
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

from vcf_parser import parse_vcf
from risk_engine import assess_risk
from llm_service import generate_explanation

load_dotenv()

app = FastAPI(
    title="PharmaGuard API",
    description="Pharmacogenomic Risk Prediction System — RIFT 2026 Hackathon",
    version="1.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "PharmaGuard API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/analyze")
async def analyze(
    vcf_file: UploadFile = File(..., description="VCF file (.vcf, max 5MB)"),
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
    if len(contents) == 0 or len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large or empty")

    try:
        vcf_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported. Please use UTF-8")

    # --- Parse VCF ---
    try:
        parsed = parse_vcf(vcf_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"VCF parsing error: {str(e)}")

    # --- Process each drug ---
    drug_list = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    if not drug_list:
        raise HTTPException(status_code=400, detail="At least one drug name is required")

    # Extract patient ID from VCF header
    patient_id = parsed.get("patient_id", "PATIENT_UNKNOWN")
    timestamp = datetime.now(timezone.utc).isoformat()

    results = []
    for drug in drug_list:
        # Risk assessment
        risk_result = assess_risk(drug, parsed["variants"], parsed["gene_diplotypes"])

        # LLM explanation
        explanation = await generate_explanation(
            drug=drug,
            risk_result=risk_result,
            variants=parsed["variants"],
        )

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
                "variants_detected_count": len(parsed["variants"]),
                "gene_coverage": list(parsed["gene_diplotypes"].keys()),
                "analysis_timestamp": timestamp,
            },
        }
        results.append(result)

    return {"results": results}
