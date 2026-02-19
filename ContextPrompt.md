# Hackathon Context Prompt — Read This First

> Paste this entire file at the start of every new AI session throughout the hackathon day.
> Update the **Current Status** section at the bottom every time you switch accounts or start a new session.

---

## Who We Are

We are a 3-person team participating in the **RIFT 2026 Hackathon**, HealthTech / Pharmacogenomics / Explainable AI Track. We are building an MVP/prototype within a single day.

---

## The Problem We Are Solving

**PharmaGuard — Pharmacogenomic Risk Prediction System**

Adverse drug reactions kill over 100,000 Americans annually. Many are preventable through pharmacogenomic testing. We are building an AI-powered web application that:

1. Parses authentic **VCF files** (Variant Call Format — genomic data standard)
2. Identifies pharmacogenomic variants across **6 critical genes:** CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
3. Predicts **drug-specific risks:** Safe / Adjust Dosage / Toxic / Ineffective / Unknown
4. Generates **clinical explanations** using LLMs with specific variant citations and biological mechanisms
5. Provides **dosing recommendations** aligned with CPIC guidelines

**Supported Drugs:** CODEINE, WARFARIN, CLOPIDOGREL, SIMVASTATIN, AZATHIOPRINE, FLUOROURACIL

---

## Our Goal

Build a working, demo-ready prototype as fast as possible. Optimizing for **speed, demo quality, exact JSON schema compliance, and pitch clarity** — not production-readiness or perfect code.

---

## Our Tech Stack

- **Frontend:** Next.js + Tailwind CSS (deployed on Vercel)
- **Backend:** Python FastAPI (deployed on Railway or Render)
- **LLM Integration:** Google Gemini API for clinical explanations
- **VCF Parsing:** Python (custom parser) in FastAPI backend
- **Database:** Supabase (only if needed — may not be necessary for this problem)
- **Deployment:** Vercel (frontend) + Railway or Render (Python FastAPI backend)
- **Version Control:** GitHub (public repo — mandatory)

---

## Mandatory Submission Checklist

> Person 3 tracks this throughout the day

- [ ] Problem statement selected on RIFT website (6–8 PM, 19th Feb)
- [ ] GitHub repository (public) with complete source code
- [ ] Live hosted URL (Vercel/Netlify/Render — publicly accessible)
- [ ] LinkedIn demo video (2–5 min, PUBLIC, must tag RIFT LinkedIn page)
- [ ] README.md with all required sections (see below)

**README Must Include:**
- Project title + description
- Live demo URL
- LinkedIn video URL
- Architecture overview
- Tech stack
- Installation & setup instructions
- API docs
- Usage examples with screenshots
- Known limitations
- Team members

---

## Critical JSON Output Schema

> This is non-negotiable. Judges test field-by-field. Every field must match exactly.

```json
{
  "patient_id": "PATIENT_XXX",
  "drug": "DRUG_NAME",
  "timestamp": "2026-02-19T14:00:00Z",
  "risk_assessment": {
    "risk_label": "Safe|Adjust Dosage|Toxic|Ineffective|Unknown",
    "confidence_score": 0.85,
    "severity": "none|low|moderate|high|critical"
  },
  "pharmacogenomic_profile": {
    "primary_gene": "CYP2D6",
    "diplotype": "*1/*4",
    "phenotype": "PM|IM|NM|RM|URM|Unknown",
    "detected_variants": [
      {
        "rsid": "rs3892097",
        "gene": "CYP2D6",
        "chromosome": "22",
        "position": 42524947,
        "ref_allele": "G",
        "alt_allele": "A",
        "genotype": "0/1",
        "star_allele": "*4",
        "clinical_significance": "Loss of function"
      }
    ]
  },
  "clinical_recommendation": {
    "action": "Use alternative drug",
    "dosing_guidance": "Avoid codeine; consider morphine or non-opioid analgesics",
    "alternative_drugs": ["morphine", "acetaminophen"],
    "monitoring": "Monitor for pain relief efficacy with alternative agents",
    "cpic_guideline": "CPIC Guideline for Codeine and CYP2D6 (2019 update)"
  },
  "llm_generated_explanation": {
    "summary": "Patient carries a CYP2D6 *1/*4 diplotype...",
    "mechanism": "CYP2D6 converts codeine to morphine. The *4 allele...",
    "evidence_level": "1A — strong evidence, CPIC Level A recommendation",
    "references": ["CPIC Guideline for CYP2D6 and Codeine Therapy (2019)"]
  },
  "quality_metrics": {
    "vcf_parsing_success": true,
    "variants_detected_count": 3,
    "gene_coverage": ["CYP2D6", "CYP2C19"],
    "analysis_timestamp": "2026-02-19T14:00:00Z"
  }
}
```

---

## Gene-Drug Mapping Reference

> Hardcode this logic. Do not guess. This is your risk engine core.

| Drug | Primary Gene | PM | IM | NM | RM | URM |
|------|-------------|-----|-----|-----|-----|-----|
| CODEINE | CYP2D6 | Ineffective | Adjust Dosage | Safe | Safe | Toxic |
| WARFARIN | CYP2C9 | Adjust Dosage | Adjust Dosage | Safe | Safe | Adjust Dosage |
| CLOPIDOGREL | CYP2C19 | Ineffective | Adjust Dosage | Safe | Safe | Safe |
| SIMVASTATIN | SLCO1B1 | Toxic | Adjust Dosage | Safe | Safe | Safe |
| AZATHIOPRINE | TPMT | Toxic | Adjust Dosage | Safe | Safe | Safe |
| FLUOROURACIL | DPYD | Toxic | Adjust Dosage | Safe | Safe | Safe |

### Severity Mapping

| Risk Label | Severity | Confidence (if known gene match) |
|-----------|----------|----------------------------------|
| Safe | none | 0.95 |
| Adjust Dosage | moderate | 0.85 |
| Toxic | critical | 0.90 |
| Ineffective | high | 0.90 |
| Unknown | low | 0.30 |

**Phenotype Codes:**
- PM = Poor Metabolizer
- IM = Intermediate Metabolizer
- NM = Normal Metabolizer
- RM = Rapid Metabolizer
- URM = Ultrarapid Metabolizer

---

## Our Team Structure

| Person | Role | Responsibilities |
|--------|------|-----------------|
| **Person 1 — The Coder** | 100% of the code | Frontend, backend, VCF parsing, LLM API integration. Single laptop, single AI session. |
| **Person 2 — UI/UX Designer** | Design only | Figma or v0.dev. File upload UI, results display, color-coded risk labels, drag-drop. Hands off designs to Person 1. |
| **Person 3 — Pitch + Product** | Strategy + submission | Owns pitch deck, demo script, LinkedIn video script, README, and submission checklist. Tracks what's built. |

---

## Decision Flow

- **Person 3** decides WHAT gets built next and tracks submission requirements
- **Person 2** decides HOW it looks
- **Person 1** executes all code with AI assistance — pure execution, no context switching

---

## How We Work

- Vibe coding — heavy AI-generated code, iterate fast
- JSON schema compliance and VCF parsing are non-negotiable — everything else is secondary
- Cut features ruthlessly
- Sync every 45 minutes for 5 minutes
- If Person 1 is blocked more than 15 minutes, all three huddle immediately

---

## What We Need From You (AI Agent)

- Write **complete, working, copy-paste-ready code** — not pseudocode or snippets
- Always write **full files**, not partial patches
- Use our tech stack unless explicitly told otherwise
- **Code first, brief explanation after**
- Warn us about common gotchas **before** they happen
- Always suggest the **simplest implementation** that works for a demo
- Flag if we are overcomplicating something
- **Do not claim something is done without verifying it works**
- When building API routes, output a one-line summary: method, path, input, output

---

## Build Priority Order

> Person 3 enforces this. Do not skip steps or build out of order.

1. **VCF file parser** — reads .vcf, extracts gene variants and rsids correctly
2. **Gene-drug risk engine** — maps variants → phenotype → risk label using hardcoded CPIC logic
3. **JSON output generator** — produces exact schema-compliant output, every field present
4. **LLM explanation integration** — Gemini API generates clinical summary per result
5. **Frontend file upload UI** — drag and drop, VCF validation, file size indicator
6. **Results display** — color-coded risk (Green=Safe, Yellow=Adjust, Red=Toxic/Ineffective), expandable sections, download JSON button, copy to clipboard
7. **Error handling** — invalid VCF messages, missing annotation handling, user-friendly errors
8. **Deployment** — Vercel frontend + Railway/Render for Python backend
9. **README + submission** — Person 3 owns this from Hour 2 onwards

---

## Color Coding Reference (UI)

| Risk Label | Color |
|-----------|-------|
| Safe | 🟢 Green |
| Adjust Dosage | 🟡 Yellow |
| Toxic | 🔴 Red |
| Ineffective | 🔴 Red |
| Unknown | ⚪ Grey |

---

## Current Status

> ⚠️ Update this section every time you start a new session or switch accounts.

### What Has Been Built So Far
```
- Nothing yet. Starting fresh.
```

### What I Need Right Now
```
[YOUR SPECIFIC REQUEST TO THE AI]
```

---

## How to Update This File Mid-Hackathon

At any natural checkpoint or before switching accounts, say:

> *"Summarize everything we've built so far and update the context prompt so I can use it in a new session."*

Then replace the **Current Status** section above with the AI's output and save this file.