### RIFT 2026 HACKATHON

```
Pharmacogenomics / Explainable AI Track
```
# PRECISION MEDICINE ALGORITHM

## PharmaGuard: Pharmacogenomic Risk Prediction

## System

```
Multi-city Hackathon • HealthTech Track
```
## PROBLEM OVERVIEW

Adverse drug reactions kill over 100,000 Americans annually. Many of these deaths are preventable
through pharmacogenomic testing — analyzing how genetic variants affect drug metabolism.
Your task is to build an AI-powered web application that analyzes patient genetic data (VCF files) and
drug names to predict personalized pharmacogenomic risks and provide clinically actionable
recommendations with LLM-generated explanations.

## CORE CHALLENGE

Build a system that:

- **1.** Parses authentic VCF files (Variant Call Format — the industry standard for genomic data)
- **2.** Identifies pharmacogenomic variants across 6 critical genes: CYP2D6, CYP2C19, CYP2C9,
    SLCO1B1, TPMT, DPYD
- **3.** Predicts drug-specific risks: Safe, Adjust Dosage, Toxic, Ineffective, Unknown
- **4.** Generates clinical explanations using LLMs with specific variant citations and biological
    mechanisms
- **5.** Provides dosing recommendations aligned with CPIC guidelines

## APPLICATION SPECIFICATIONS

### Input Requirements

**1. VCF File Upload**
    - File format: .vcf (Variant Call Format v4.2)
    - File size: Up to 5 MB
    - Structure: Standard VCF with INFO tags (GENE, STAR, RS)
    - Sample files provided in public test cases


**2. Drug Name Input**
    - Format: Text input field
    - Support: Single drug or multiple drugs (comma-separated)
    - Supported drugs: CODEINE, WARFARIN, CLOPIDOGREL, SIMVASTATIN, AZATHIOPRINE,
       FLUOROURACIL
    - Optional: Support for additional drugs

### Output Requirements

Your application MUST generate structured JSON output matching this EXACT schema:
{ "patient_id": "PATIENT_XXX",
"drug": "DRUG_NAME",
"timestamp": "ISO8601_timestamp",
"risk_assessment": { "risk_label": "Safe|Adjust Dosage|Toxic|...",
"confidence_score": 0.0, "severity": "none|low|moderate|high|critical" },
"pharmacogenomic_profile": { "primary_gene": "GENE_SYMBOL",
"diplotype": "*X/*Y", "phenotype": "PM|IM|NM|RM|URM|Unknown",
"detected_variants": [ { "rsid": "rsXXXX", ... } ] },
"clinical_recommendation": { ... },
"llm_generated_explanation": { "summary": "...", ... },
"quality_metrics": { "vcf_parsing_success": true, ... }
}

### Web Interface Requirements

**1. File Upload Interface**
    - Drag-and-drop or file picker
    - VCF file validation before processing
    - File size limit indicator
**2. Drug Input Field**
    - Text input or dropdown selection
    - Support for multiple drugs (comma-separated or multi-select)
    - Input validation
**3. Results Display**
    - Clear visual presentation of risk assessment
    - Color-coded risk labels (Green = Safe, Yellow = Adjust, Red = Toxic/Ineffective)
    - Expandable sections for detailed information
    - Downloadable JSON output + Copy-to-clipboard functionality
**4. Error Handling**
    - Clear error messages for invalid VCF files
    - Graceful handling of missing annotations
    - User-friendly error explanations


## MANDATORY SUBMISSION REQUIREMENTS

```
⚠ CRITICAL: You MUST submit ALL of the following to be eligible for evaluation.
Missing any component will result in DISQUALIFICATION.
# Requirement Details
1 Live Deployed Web Application
URL
Must be publicly accessible. Supported platforms: Vercel,
Netlify, Render, AWS, GCP, Azure. Include URL in
README.md.
2 LinkedIn Video Demonstration 2–5 min video. Must tag RIFT official LinkedIn page.
Hashtags: #RIFT2026 #PharmaGuard #Pharmacogenomics
#AIinHealthcare. Must be PUBLIC.
3 GitHub Repository Complete public repo with all source code, README.md,
requirements.txt / package.json, .env.example, deployment
instructions, sample VCF files.
4 Comprehensive README.md Must include: Project title, Live demo link, LinkedIn video link,
Architecture overview, Tech stack, Installation instructions,
API docs, Usage examples, Team members.
```
## SUBMISSION FIELDS

Submit through the official RIFT website (19th Feb, 6–8 PM window) with the following:

- Problem Statement selected (on RIFT website during the submission window)
- GitHub Repository URL
- Hosted / Live Application URL
- Demo video link posted on LinkedIn tagging RIFT's official page

## EVALUATION CRITERIA

```
Criterion Description
Problem Clarity Clear understanding and framing of the
pharmacogenomics problem
Solution Accuracy Correct risk predictions, valid JSON output schema
compliance
Technical Depth VCF parsing quality, LLM integration strategy, CPIC
alignment
Innovation & Thinking Creative approaches to explainability and clinical UX
Presentation (Demo Video) Architecture walkthrough, live demo quality, clarity of
explanation
```

```
Test Cases Exact field-by-field match with expected JSON outputs
from test VCF files
Documentation Complete README with all required sections, setup
instructions, API docs
```
## DISQUALIFICATION CRITERIA

```
⚠ Submissions will be DISQUALIFIED for any of the following:
```
- No live deployed URL provided
- Live application is not accessible or functional
- LinkedIn video not posted or not public
- Video does not tag the RIFT2026 page
- GitHub repository is private or incomplete
- README.md missing required links
- Application does not accept VCF file uploads
- JSON output does not match required schema
- Submission after 12:00 PM deadline

### Good luck! May your algorithms save lives.

```
— RIFT 2026 Organizing Team
```