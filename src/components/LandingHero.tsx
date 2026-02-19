"use client";

import { useRef, useState } from "react";
import { Upload, FileText, Loader2, Play, ShieldPlus, ChevronRight } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";

interface LandingHeroProps {
    file: File | null;
    onFileChange: (file: File | null) => void;
    selectedDrugs: string[];
    onDrugToggle: (drug: string) => void;
    onAnalyze: () => void;
    loading: boolean;
    error: string | null;
    supportedDrugs: string[];
}

const DRUG_ICONS: Record<string, string> = {
    CODEINE: "💊",
    WARFARIN: "💧",
    CLOPIDOGREL: "❤️",
    SIMVASTATIN: "🧬",
    AZATHIOPRINE: "🛡️",
    FLUOROURACIL: "🔬",
};

export function LandingHero({
    file,
    onFileChange,
    selectedDrugs,
    onDrugToggle,
    onAnalyze,
    loading,
    error,
    supportedDrugs,
}: LandingHeroProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [dragOver, setDragOver] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
        if (e.dataTransfer.files?.[0]) {
            onFileChange(e.dataTransfer.files[0]);
        }
    };

    const ready = !!file && selectedDrugs.length > 0;

    return (
        <div className="relative min-h-[calc(100vh-64px)] flex flex-col md:flex-row items-center justify-center p-6 md:p-12 gap-12 max-w-7xl mx-auto">

            {/* Left Column: Hero Text */}
            <div className="flex-1 space-y-8 text-center md:text-left">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-teal-50 border border-teal-100 rounded-full text-teal-700 text-sm font-semibold mb-6">
                        <ShieldPlus className="w-4 h-4" />
                        <span>Clinical Decision Support System</span>
                    </div>
                    <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-slate-900 mb-6 leading-tight">
                        Precision Medicine <br />
                        <span className="text-teal-600">at the Point of Care</span>
                    </h1>
                    <p className="text-lg text-slate-600 max-w-xl leading-relaxed">
                        Advanced pharmacogenomic risk stratification for clinicians.
                        Upload patient VCF data to instantly screen for CPIC Level A interactions
                        across critical therapeutic areas.
                    </p>
                </motion.div>

                <div className="flex flex-col md:flex-row gap-4 justify-center md:justify-start">
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                        HIPAA Compliant
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                        Local Processing
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                        2026 Guidelines
                    </div>
                </div>
            </div>

            {/* Right Column: Intake Card */}
            <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="flex-1 w-full max-w-lg"
            >
                <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
                    <div className="bg-slate-50 border-b border-slate-100 p-4 flex justify-between items-center">
                        <h3 className="font-semibold text-slate-700 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-slate-400" />
                            New Analysis Request
                        </h3>
                        <div className="text-xs font-mono text-slate-400">ID: {Math.random().toString(36).substr(2, 9).toUpperCase()}</div>
                    </div>

                    <div className="p-6 md:p-8 space-y-8">
                        {/* Step 1 */}
                        <div className="space-y-4">
                            <label className="text-sm font-bold text-slate-900 flex items-center justify-between">
                                <span>1. Patient Genomic Data</span>
                                <span className="text-xs font-normal text-slate-500 uppercase tracking-wider">Required</span>
                            </label>

                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current?.click()}
                                className={cn(
                                    "border-2 border-dashed rounded-xl p-8 transition-all duration-200 cursor-pointer text-center relative group",
                                    dragOver ? "border-teal-500 bg-teal-50" : "border-slate-300 bg-slate-50 hover:border-teal-400 hover:bg-slate-100",
                                    file ? "border-emerald-500 bg-emerald-50" : ""
                                )}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".vcf"
                                    className="hidden"
                                    onChange={(e) => {
                                        if (e.target.files?.[0]) onFileChange(e.target.files[0]);
                                    }}
                                />

                                <AnimatePresence mode="wait">
                                    {file ? (
                                        <motion.div
                                            key="file"
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            className="flex flex-col items-center gap-3"
                                        >
                                            <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center">
                                                <FileText className="w-6 h-6" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-slate-900">{file.name}</p>
                                                <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                                            </div>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); onFileChange(null); }}
                                                className="text-xs text-red-500 hover:text-red-700 font-medium underline decoration-red-200 underline-offset-4"
                                            >
                                                Remove
                                            </button>
                                        </motion.div>
                                    ) : (
                                        <motion.div
                                            key="empty"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="space-y-3 pointer-events-none"
                                        >
                                            <div className="w-12 h-12 bg-white border border-slate-200 text-slate-400 rounded-xl flex items-center justify-center mx-auto shadow-sm group-hover:scale-110 transition-transform">
                                                <Upload className="w-6 h-6" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-slate-700">Drop VCF file here</p>
                                                <p className="text-xs text-slate-400">or click to browse</p>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* Step 2 */}
                        <div className="space-y-4">
                            <label className="text-sm font-bold text-slate-900 flex items-center justify-between">
                                <span>2. Target Medications</span>
                                <span className="text-xs font-normal text-slate-500 uppercase tracking-wider">Select at least one</span>
                            </label>

                            <div className="grid grid-cols-2 gap-2">
                                {supportedDrugs.map((drug) => {
                                    const isSelected = selectedDrugs.includes(drug);
                                    return (
                                        <button
                                            key={drug}
                                            onClick={() => onDrugToggle(drug)}
                                            className={cn(
                                                "px-3 py-2.5 rounded-lg text-sm font-medium text-left transition-all flex items-center gap-2",
                                                isSelected
                                                    ? "bg-teal-600 text-white shadow-md ring-2 ring-teal-600 ring-offset-1"
                                                    : "bg-white border border-slate-200 text-slate-600 hover:border-teal-300 hover:bg-teal-50"
                                            )}
                                        >
                                            <span className="opacity-80">{DRUG_ICONS[drug]}</span>
                                            {drug}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600 flex items-center gap-2">
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        {/* Action */}
                        <button
                            onClick={onAnalyze}
                            disabled={!ready || loading}
                            className={cn(
                                "w-full py-3.5 rounded-xl font-bold text-base flex items-center justify-center gap-2 transition-all shadow-lg",
                                ready && !loading
                                    ? "bg-slate-900 text-white hover:bg-slate-800 hover:shadow-xl hover:-translate-y-0.5"
                                    : "bg-slate-100 text-slate-400 cursor-not-allowed shadow-none"
                            )}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Starting Analysis...
                                </>
                            ) : (
                                <>
                                    <Play className="w-4 h-4 fill-current" />
                                    Run Analysis
                                    <ChevronRight className="w-4 h-4 opacity-50" />
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
