"use client";

import { useState, useCallback, useEffect } from "react";
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
  cpic_data?: {
    recommendation: string | null;
    classification: string | null;
    evidence_level: string | null;
    guideline_name: string | null;
    guideline_url: string | null;
    implications: Record<string, string> | null;
    data_source: string;
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

interface CpicDrug {
  drugname: string;
  genesymbol: string;
  guidelinename: string;
  guidelineurl: string;
  cpiclevel: string;
  supported: boolean;
}

const FEATURED_DRUGS = [
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
  const [cpicDrugs, setCpicDrugs] = useState<CpicDrug[]>([]);

  // Fetch CPIC Level A drugs on mount — with cleanup to prevent stale data
  useEffect(() => {
    const controller = new AbortController();

    fetch(`${API_URL}/api/cpic/level-a-drugs`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => setCpicDrugs(data.drugs || []))
      .catch(() => { });

    return () => controller.abort();
  }, []);

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

  // --- Drug toggle (functional setState — stable callback) ---
  const toggleDrug = useCallback((drug: string) => {
    setSelectedDrugs((prev) =>
      prev.includes(drug) ? prev.filter((d) => d !== drug) : [...prev, drug]
    );
  }, []);

  // --- Submit ---
  const handleSubmit = useCallback(async () => {
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
  }, [file, selectedDrugs]);

  const handleProcessingComplete = useCallback(() => {
    setProcessing(false);
  }, []);

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
  const handleClearContext = useCallback(() => {
    setFile(null);
    setSelectedDrugs([]);
    setResults([]);
    setError(null);
    setLoading(false);
    setProcessing(false);
    setCopied(false);
  }, []);

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
        supportedDrugs={FEATURED_DRUGS}
        cpicDrugs={cpicDrugs}
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
            <h1 className="text-2xl font-bold text-slate-900">Drug interaction report</h1>
            <span className="text-sm text-slate-500">Generated on {new Date().toLocaleDateString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyJson} aria-label="Copy JSON to clipboard"
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-colors duration-200 shadow-sm"
            >
              {copied ? (
                <><CheckCheck className="w-4 h-4 text-emerald-600" /> Copied!</>
              ) : (
                <><Copy className="w-4 h-4" /> Copy as JSON</>
              )}
            </button>
            <button
              onClick={handleDownloadJson} aria-label="Download JSON report"
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors duration-200 shadow-sm"
            >
              <Download className="w-4 h-4" />
              Download report
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
              cpicLevel={result.cpic_data?.evidence_level || null}
              dataSource={result.cpic_data?.data_source || "Local fallback"}
            />
            <ActionPanel
              recommendation={result.clinical_recommendation}
              explanation={result.llm_generated_explanation}
              variants={result.pharmacogenomic_profile.detected_variants}
              cpicData={result.cpic_data || null}
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
