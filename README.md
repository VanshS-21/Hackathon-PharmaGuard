# 🧬 PharmaGuard — Pharmacogenomic Risk Prediction System

> An AI-powered web application that analyzes patient genetic data (VCF files) to predict personalized drug risks and provide CPIC-aligned clinical recommendations.

**RIFT 2026 Hackathon** — HealthTech / Pharmacogenomics Track

---

## 🔗 Links

- **GitHub:** [https://github.com/VanshS-21/Hackathon-PharmaGuard](https://github.com/VanshS-21/Hackathon-PharmaGuard)
- **API Docs:** `http://localhost:8000/docs` (Swagger UI, auto-generated)

---

## 📖 What It Does

Adverse drug reactions kill over 100,000 patients annually — many are preventable through pharmacogenomics. **PharmaGuard** analyzes a patient's VCF file to:

1. **Parse VCF** and extract pharmacogenomic variants (supports VCF v4.2)
2. **Call star alleles & diplotypes** using CPIC allele definitions
3. **Predict phenotype** (PM / IM / NM / RM / UM) per gene
4. **Assess drug risk** (Safe / Adjust Dosage / Toxic / Ineffective / Unknown)
5. **Generate clinical explanations** grounded in CPIC guidelines via Gemini LLM
6. **Return structured JSON** matching the exact hackathon output schema

### Supported Genes & Drugs

| Gene | Drug |
|------|------|
| CYP2D6 | CODEINE |
| CYP2C9 | WARFARIN |
| CYP2C19 | CLOPIDOGREL |
| SLCO1B1 | SIMVASTATIN |
| TPMT | AZATHIOPRINE |
| DPYD | FLUOROURACIL |

---

## 🏗️ Architecture

```
┌───────────────────────────────┐
│   Next.js 15 Frontend (3000)  │
│   TypeScript + Tailwind CSS   │
└──────────────┬────────────────┘
               │  POST /api/analyze (multipart VCF + drugs)
┌──────────────▼────────────────┐
│   FastAPI Backend (8000)      │
│                               │
│  vcf_parser.py                │
│  ├─ VCF v4.2 validation       │
│  ├─ INFO field parsing        │
│  ├─ Genotype calling (GT)     │
│  └─ Star allele diplotyping   │
│                               │
│  risk_engine.py               │
│  ├─ CPIC phenotype mapping    │
│  ├─ Drug-gene risk rules      │
│  └─ CPIC API enrichment       │
│                               │
│  llm_service.py               │
│  └─ Gemini 2.0 Flash + CPIC   │
└───────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.10+
- **Google Gemini API Key** (free at [aistudio.google.com](https://aistudio.google.com))

### 1. Clone
```bash
git clone https://github.com/VanshS-21/Hackathon-PharmaGuard.git
cd Hackathon-PharmaGuard
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URI=http://localhost:3000
```

Start backend:
```bash
uvicorn main:app --reload --port 8000
```
> API docs available at: http://localhost:8000/docs

### 3. Frontend Setup
```bash
# From project root
npm install
```

Create `.env.local` in project root:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

Start frontend:
```bash
npm run dev
```

Open **http://localhost:3000**

---

## 📡 API Reference

### `POST /api/analyze`

Analyze a VCF file for one or more drugs.

**Request** (`multipart/form-data`):
| Field | Type | Description |
|-------|------|-------------|
| `vcf_file` | File | VCF v4.2 file (`.vcf`, max 5 MB) |
| `drugs` | string | Comma-separated drugs, e.g. `CODEINE,WARFARIN` |

**Response** (`200 OK` — JSON array):
```json
[
  {
    "patient_id": "PATIENT_001",
    "drug": "CODEINE",
    "timestamp": "2026-02-20T04:00:00+00:00",
    "risk_assessment": {
      "risk_label": "Safe",
      "confidence_score": 0.95,
      "severity": "none"
    },
    "pharmacogenomic_profile": {
      "primary_gene": "CYP2D6",
      "diplotype": "*1/*2",
      "phenotype": "NM",
      "detected_variants": [
        {
          "rsid": "rs16947",
          "gene": "CYP2D6",
          "chromosome": "chr22",
          "position": 42128945,
          "ref_allele": "C",
          "alt_allele": "T",
          "genotype": "0/1",
          "star_allele": "*2",
          "clinical_significance": "Normal function"
        }
      ]
    },
    "clinical_recommendation": {
      "action": "Use as directed",
      "dosing_guidance": "Standard dosing per label",
      "alternative_drugs": [],
      "monitoring": "Routine monitoring",
      "cpic_guideline": "CPIC Guideline for CYP2D6 and Codeine Therapy (2019)"
    },
    "llm_generated_explanation": {
      "summary": "...",
      "mechanism": "...",
      "evidence_level": "1A — strong evidence, CPIC Level A recommendation",
      "references": ["CPIC Guideline for CYP2D6 and CODEINE Therapy", "PharmGKB (https://www.pharmgkb.org)"]
    },
    "quality_metrics": {
      "vcf_parsing_success": true,
      "variants_detected_count": 1,
      "gene_coverage": ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"],
      "analysis_timestamp": "2026-02-20T04:00:00+00:00"
    }
  }
]
```

**Error Responses:**
| Code | Reason |
|------|--------|
| `400` | Invalid VCF format, missing GENE=/STAR= tags, or unsupported gene |
| `422` | Missing required fields |
| `429` | Rate limit exceeded (10 req/min) |
| `500` | Internal server error |

### Other Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/drugs` | List supported drugs |
| `GET /api/genes` | List supported genes |
| `GET /api/cpic/level-a-drugs` | CPIC Level A gene-drug pairs |

---

## 📁 Project Structure

```
hackathon-pharmaguard/
├── backend/                  # Python FastAPI backend
│   ├── main.py               # FastAPI app + /api/analyze endpoint
│   ├── vcf_parser.py         # VCF v4.2 parser + star allele diplotyping
│   ├── risk_engine.py        # Phenotype-to-risk mapping + CPIC enrichment
│   ├── cpic_service.py       # CPIC API client (with caching)
│   ├── llm_service.py        # Gemini LLM integration + fallback
│   ├── drug_rules.json       # Drug-gene-phenotype risk rules
│   ├── variant_database.json # rs ID → star allele → function mapping
│   ├── requirements.txt      # Python dependencies
│   └── test_parser_spec.py   # VCF parser specification tests
│
├── src/                      # Next.js frontend
│   ├── app/
│   │   └── page.tsx          # Main application page
│   └── components/           # UI components
│       ├── LandingHero.tsx
│       ├── TriageBanner.tsx
│       ├── ActionPanel.tsx
│       ├── PatientContextBar.tsx
│       ├── PatientHistory.tsx
│       └── ui/ProcessingState.tsx
│
├── sample/                   # Sample VCF files for testing
│   ├── TC_P1_PATIENT_001_Normal.vcf   # Hackathon test case
│   └── sample2.vcf ... sample12.vcf  # Additional edge cases
│
├── .env.example              # Environment variable template
├── ProblemStatement.md       # Hackathon problem statement
└── README.md                 # This file
```

---

## 🧪 Testing

### Run VCF Parser Spec Tests
```bash
cd backend
python test_parser_spec.py
```

### Test with the Judge's TC_P1 file
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "vcf_file=@sample/TC_P1_PATIENT_001_Normal.vcf" \
  -F "drugs=CODEINE,WARFARIN,CLOPIDOGREL,SIMVASTATIN,AZATHIOPRINE,FLUOROURACIL"
```

Expected for TC_P1: All 6 drugs → `risk_label: "Safe"`, `phenotype: "NM"`, CYP2D6 diplotype `*1/*2`.

---

## ⚠️ VCF File Requirements

VCF files **must**:
- Start with `##fileformat=VCFv4.2`
- Have a `#CHROM` header with at least 10 columns (including FORMAT + sample)
- Have `GENE=` and `STAR=` INFO tags on every data row
- Use recognized gene names: `CYP2D6`, `CYP2C19`, `CYP2C9`, `SLCO1B1`, `TPMT`, `DPYD`
- Have max 2 variants per gene
- REF allele must not be `.`
- INFO column must not be `.`

---

## 👥 Team

| Name | Role |
|------|------|
| Vansh S. | Full-stack Development, VCF Parsing, Backend API, LLM Integration |

---

## 📄 License

Built for RIFT 2026 Hackathon. MIT License.

> **Disclaimer:** PharmaGuard is a prototype built for educational and demonstration purposes. Not intended for clinical use.
