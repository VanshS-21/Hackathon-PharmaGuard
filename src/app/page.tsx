"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Download, Copy, CheckCheck } from "lucide-react";
import { LandingHero } from "@/components/LandingHero";
import { PatientContextBar } from "@/components/PatientContextBar";
import { TriageBanner } from "@/components/TriageBanner";
import { ActionPanel } from "@/components/ActionPanel";
import { ProcessingState } from "@/components/ui/ProcessingState";

// --- Types ---
interface DetectedVariant {
  rsid: string;
  gene: string;
  chromosome: string;
  position: number;
  ref_allele: string;
  alt_allele: string;
  genotype: string;
  star_allele: string;
  clinical_significance: string;
}

interface DrugResult {
  patient_id: string;
  drug: string;
  timestamp: string;
  risk_assessment: {
    risk_label: string;
    confidence_score: number;
    severity: string;
  };
  pharmacogenomic_profile: {
    primary_gene: string;
    diplotype: string;
    phenotype: string;
    detected_variants: DetectedVariant[];
  };
  clinical_recommendation: {
    action: string;
    dosing_guidance: string;
    alternative_drugs: string[];
    monitoring: string;
    cpic_guideline: string;
  };
  llm_generated_explanation: {
    summary: string;
    mechanism: string;
    evidence_level: string;
    references: string[];
  };
  quality_metrics: {
    vcf_parsing_success: boolean;
    variants_detected_count: number;
    gene_coverage: string[];
    analysis_timestamp: string;
  };
}

const SUPPORTED_DRUGS = [
  "CODEINE",
  "WARFARIN",
  "CLOPIDOGREL",
  "SIMVASTATIN",
  "AZATHIOPRINE",
  "FLUOROURACIL",
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>([]);
  const [results, setResults] = useState<DrugResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false); // New Processing State
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // --- File handlers ---
  const handleFileChange = useCallback((f: File | null) => {
    setError(null);
    if (!f) {
      setFile(null);
      return;
    }
    if (!f.name.toLowerCase().endsWith(".vcf")) {
      setError("Invalid file format. Only .vcf files accepted");
      return;
    }
    if (f.size === 0 || f.size > 5 * 1024 * 1024) {
      setError("File too large or empty");
      return;
    }
    setFile(f);
  }, []);

  // --- Drug toggle ---
  const toggleDrug = (drug: string) => {
    setSelectedDrugs((prev) =>
      prev.includes(drug) ? prev.filter((d) => d !== drug) : [...prev, drug]
    );
  };

  // --- Submit ---
  const handleSubmit = async () => {
    if (!file || selectedDrugs.length === 0) return;
    setLoading(true);
    setError(null);

    // START Processing Visuals
    setProcessing(true);

    try {
      const formData = new FormData();
      formData.append("vcf_file", file);
      formData.append("drugs", selectedDrugs.join(","));

      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Server error" }));
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();
      // Wait for visuals to finish before showing
      setResults(data.results);
      // Processing state will be turned off by the callback on ProcessingState component
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
      setProcessing(false);
    }
  };

  const handleProcessingComplete = () => {
    setProcessing(false);
  };

  // --- Export: Download JSON ---
  const handleDownloadJson = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pharmaguard-report-${results[0]?.patient_id || "unknown"}-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // --- Export: Copy JSON to Clipboard ---
  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(results, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const ta = document.createElement("textarea");
      ta.value = JSON.stringify(results, null, 2);
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // --- Reset ---
  const handleClearContext = () => {
    setFile(null);
    setSelectedDrugs([]);
    setResults([]);
    setError(null);
    setLoading(false);
    setProcessing(false);
    setCopied(false);
  };

  // --- Render: Processing State ---
  if (processing) {
    return <ProcessingState onComplete={handleProcessingComplete} />;
  }

  // --- Render: Landing Page State ---
  if (results.length === 0) {
    return (
      <LandingHero
        file={file}
        onFileChange={handleFileChange}
        selectedDrugs={selectedDrugs}
        onDrugToggle={toggleDrug}
        onAnalyze={handleSubmit}
        loading={loading}
        error={error}
        supportedDrugs={SUPPORTED_DRUGS}
      />
    );
  }

  // --- Render: Dashboard State ---
  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      <PatientContextBar
        patientId={results[0]?.patient_id || "Unknown"}
        onClear={handleClearContext}
      />

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Analysis Results</h1>
            <span className="text-sm text-slate-500">Generated {new Date().toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyJson}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm"
            >
              {copied ? (
                <><CheckCheck className="w-4 h-4 text-emerald-600" /> Copied!</>
              ) : (
                <><Copy className="w-4 h-4" /> Copy JSON</>
              )}
            </button>
            <button
              onClick={handleDownloadJson}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-all shadow-sm"
            >
              <Download className="w-4 h-4" />
              Download JSON
            </button>
          </div>
        </div>

        {results.map((result, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: idx * 0.1, ease: "easeOut" }}
            className="rounded-xl shadow-sm border border-slate-200 overflow-hidden"
          >
            <TriageBanner
              riskLabel={result.risk_assessment.risk_label}
              drugName={result.drug}
              gene={result.pharmacogenomic_profile.primary_gene}
              phenotype={result.pharmacogenomic_profile.phenotype}
            />
            <ActionPanel
              recommendation={result.clinical_recommendation}
              explanation={result.llm_generated_explanation}
              variants={result.pharmacogenomic_profile.detected_variants}
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
