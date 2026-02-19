# 🧬 PharmaGuard — Pharmacogenomic Risk Prediction System

> AI-powered web application that analyzes patient genetic data (VCF files) to predict personalized drug risks and provide clinically actionable recommendations.

**RIFT 2026 Hackathon** — HealthTech / Pharmacogenomics / Explainable AI Track

---

## 🔗 Links

- **Live Demo:** [Coming Soon — will be deployed on Vercel]
- **LinkedIn Demo Video:** [Coming Soon — 2-5 min video]
- **GitHub Repo:** [https://github.com/VanshS-21/Hackathon-PharmaGuard](https://github.com/VanshS-21/Hackathon-PharmaGuard)

---

## 📖 Project Description

Adverse drug reactions kill over 100,000 Americans annually. Many are preventable through pharmacogenomic testing. **PharmaGuard** analyzes patient VCF (Variant Call Format) files to:

1. **Parse VCF files** and extract pharmacogenomic variants
2. **Identify risk variants** across 6 critical genes: CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
3. **Predict drug-specific risks**: Safe, Adjust Dosage, Toxic, Ineffective, Unknown
4. **Generate clinical explanations** using LLMs with variant citations and biological mechanisms
5. **Provide dosing recommendations** aligned with CPIC guidelines

### Supported Drugs
`CODEINE` · `WARFARIN` · `CLOPIDOGREL` · `SIMVASTATIN` · `AZATHIOPRINE` · `FLUOROURACIL`

---

## 🏗️ Architecture Overview

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Next.js        │     │   API Routes     │     │   LLM API        │
│   Frontend       │────▶│   (Backend)      │────▶│   (Claude/GPT)   │
│   Tailwind CSS   │     │                  │     │                  │
└──────────────────┘     └────────┬─────────┘     └──────────────────┘
                                  │
                         ┌────────▼─────────┐
                         │   VCF Parser     │
                         │   + Risk Engine  │
                         │   (CPIC Logic)   │
                         └──────────────────┘
```

**Flow:** Upload VCF → Parse Variants → Map to Phenotypes → Predict Risk → Generate LLM Explanation → Display Results

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + React + TypeScript |
| Styling | Tailwind CSS |
| Backend | Python FastAPI |
| LLM Integration | Google Gemini API |
| VCF Parsing | Custom Python parser |
| Deployment | Vercel (frontend) + Railway/Render (backend) |
| Version Control | GitHub (public) |

---

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- npm or yarn

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/VanshS-21/Hackathon-PharmaGuard.git
cd Hackathon-PharmaGuard

# 2. Frontend setup
npm install
cp .env.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Backend setup
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env — add your GEMINI_API_KEY

# 4. Run backend
uvicorn main:app --reload --port 8000

# 5. Run frontend (in a new terminal)
cd ..  # back to project root
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📡 API Documentation

### `POST /api/analyze`

Analyzes a VCF file against specified drugs and returns pharmacogenomic risk predictions.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `vcfFile` (File) — VCF file (.vcf, max 5MB)
  - `drugs` (string) — Comma-separated drug names (e.g., `CODEINE,WARFARIN`)

**Response:** JSON object matching the schema defined in the problem statement (see `ContextPrompt.md` for full schema).

---

## 📸 Usage Examples

> Screenshots will be added once the UI is built.

1. **Upload a VCF file** via drag-and-drop or file picker
2. **Enter drug name(s)** — e.g., CODEINE, WARFARIN
3. **View results** — color-coded risk labels with expandable clinical details
4. **Download JSON** or copy results to clipboard

---

## ⚠️ Known Limitations

- Supports only 6 drugs and 6 genes (as per problem statement)
- VCF files must include INFO tags: GENE, STAR, RS
- LLM-generated explanations require an active API key
- Not intended for real clinical use — prototype/demo only
- Star allele calling is simplified (not full PharmVar)

---

## 👥 Team Members

| Name | Role |
|------|------|
| Person 1 | Coder — Frontend, Backend, VCF Parsing, LLM Integration |
| Person 2 | UI/UX Designer — Figma / v0.dev |
| Person 3 | Pitch + Product — Deck, Video, README, Submissions |

---

## 📄 License

Built for RIFT 2026 Hackathon. MIT License.
