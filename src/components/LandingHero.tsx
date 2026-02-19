"use client";

import { useRef, useState, useMemo, useId } from "react";
import {
    Upload, FileText, Loader2, Play, ShieldPlus, ChevronRight,
    Search, Check, X, ExternalLink, AlertTriangle,
    Pill, Droplets, Heart, Dna, ShieldCheck, Microscope,
    ScanLine, Binary, Cpu
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";
import { DnaHelix } from "@/components/ui/DnaHelix";

interface CpicDrug {
    drugname: string;
    genesymbol: string;
    guidelinename: string;
    guidelineurl: string;
    cpiclevel: string;
    supported: boolean;
}

interface LandingHeroProps {
    file: File | null;
    onFileChange: (file: File | null) => void;
    selectedDrugs: string[];
    onDrugToggle: (drug: string) => void;
    onAnalyze: () => void;
    loading: boolean;
    error: string | null;
    supportedDrugs: string[];
    cpicDrugs: CpicDrug[];
}

const DRUG_ICONS: Record<string, React.ReactNode> = {
    CODEINE: <Pill className="w-4 h-4" />,
    WARFARIN: <Droplets className="w-4 h-4" />,
    CLOPIDOGREL: <Heart className="w-4 h-4" />,
    SIMVASTATIN: <Dna className="w-4 h-4" />,
    AZATHIOPRINE: <ShieldCheck className="w-4 h-4" />,
    FLUOROURACIL: <Microscope className="w-4 h-4" />,
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
    cpicDrugs,
}: LandingHeroProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [dragOver, setDragOver] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [showDropdown, setShowDropdown] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

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

    // Stable ID for hydration safety
    const formId = useId();

    const filteredCpicDrugs = useMemo(() => {
        if (!searchQuery.trim()) return [];
        const q = searchQuery.toLowerCase();
        const featured = new Set(supportedDrugs.map(d => d.toLowerCase()));
        return cpicDrugs
            .filter(d => d.drugname && !featured.has(d.drugname))
            .filter(d =>
                (d.drugname || "").includes(q) ||
                (d.genesymbol || "").toLowerCase().includes(q) ||
                (d.guidelinename || "").toLowerCase().includes(q)
            )
            .slice(0, 12);
    }, [searchQuery, cpicDrugs, supportedDrugs]);

    const ready = !!file && selectedDrugs.length > 0;

    const handleBlur = () => {
        setTimeout(() => setShowDropdown(false), 200);
    };

    return (
        <div className="relative min-h-[calc(100vh-64px)] flex flex-col md:flex-row items-center justify-center p-6 md:p-12 gap-12 max-w-7xl mx-auto">

            {/* Full-page DNA helix background — diagonal bottom-left → top-right */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none z-0 flex items-center justify-center opacity-70">
                <div style={{ transform: "rotate(-35deg)" }}>
                    <DnaHelix
                        width={400}
                        height={1400}
                        opacity={0.04}
                        speed={0.5}
                        className="hidden md:block"
                    />
                </div>
            </div>

            {/* Left Column: Hero Text */}
            <div className="flex-1 space-y-8 text-center md:text-left relative z-10">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30, delay: 0.05 }}
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-700 text-slate-300 text-xs font-mono mb-6 tracking-wider uppercase">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 blink"></span>
                        Ready
                    </div>
                    <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-slate-900 mb-6 leading-tight">
                        Pharmacogenomic <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-cyan-600">
                            Risk Analysis
                        </span>
                    </h1>
                    <p className="text-lg text-slate-600 max-w-xl leading-relaxed font-mono text-sm border-l-2 border-slate-200 pl-4">
                        Detect drug-gene interactions in seconds.<br />
                        Backed by CPIC Level A guidelines.<br />
                        Your data never leaves this device.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30, delay: 0.2 }}
                    className="flex flex-col md:flex-row gap-8 justify-center md:justify-start"
                >
                    <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-xs font-mono text-slate-500">
                        <div className="flex items-center gap-2">
                            <Check className="w-3 h-3 text-emerald-500" />
                            HIPAA compliant
                        </div>
                        <div className="flex items-center gap-2">
                            <Check className="w-3 h-3 text-emerald-500" />
                            Runs locally
                        </div>
                        <div className="flex items-center gap-2">
                            <Check className="w-3 h-3 text-emerald-500" />
                            CPIC 2026 database
                        </div>
                        <div className="flex items-center gap-2">
                            <Check className="w-3 h-3 text-emerald-500" />
                            Data encrypted
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6, duration: 1 }}
                    className="pt-16 hidden md:block"
                >
                    <div className="flex items-center gap-4 text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                        <div className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                            System Operational
                        </div>
                        <div className="w-px h-3 bg-slate-300"></div>
                        <div className="flex items-center gap-2">
                            <Cpu className="w-3 h-3 text-slate-400" />
                            Local Processing
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Right Column: Intake Card */}
            <motion.div
                initial={{ opacity: 0, skewY: 2 }}
                animate={{ opacity: 1, skewY: 0 }}
                transition={{ type: "spring", stiffness: 260, damping: 28, delay: 0.15 }}
                className="flex-1 w-full max-w-lg"
            >
                <div className="panel-tech p-1">
                    <div className="bg-slate-50/50 p-3 border-b border-slate-200 flex justify-between items-center backdrop-blur-sm">
                        <h3 className="text-xs font-bold text-slate-700 flex items-center gap-2 font-mono uppercase tracking-wider">
                            <Binary className="w-4 h-4 text-slate-400" />
                            New Analysis
                        </h3>
                        <div className="text-[10px] font-mono text-slate-400">
                            ID: {formId.replace(/:/g, "").toUpperCase().slice(0, 9)}
                        </div>
                    </div>

                    <div className="p-6 md:p-8 space-y-8 bg-white/40">
                        {/* Step 1 */}
                        <div className="space-y-4">
                            <label className="text-xs font-bold text-slate-900 flex items-center justify-between font-mono uppercase">
                                <span>1. Upload your VCF file</span>
                                <span className={cn("text-[10px] px-1.5 py-0.5 rounded", file ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-500")}>
                                    {file ? "File ready" : "Required"}
                                </span>
                            </label>

                            <div
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current?.click()}
                                className={cn(
                                    "border-2 border-dashed rounded-none p-8 transition-all duration-300 cursor-pointer text-center relative group overflow-hidden",
                                    dragOver ? "border-teal-500 bg-teal-50/50" : "border-teal-500/30 bg-teal-50/5 hover:border-teal-400 hover:bg-teal-50/20 hover:shadow-[0_0_20px_rgba(20,184,166,0.15)]",
                                    file ? "border-emerald-500 bg-emerald-50/30 border-solid shadow-none hover:shadow-none" : ""
                                )}
                            >
                                <div className="absolute inset-0 pointer-events-none opacity-20 bg-[url('/grid.svg')] bg-[length:10px_10px]"></div>
                                {dragOver && <div className="scanline"></div>}

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
                                            className="flex flex-col items-center gap-3 relative z-10"
                                        >
                                            <div className="w-12 h-12 bg-emerald-100/50 text-emerald-600 flex items-center justify-center border border-emerald-200">
                                                <Binary className="w-6 h-6" />
                                            </div>
                                            <div className="font-mono">
                                                <p className="font-bold text-xs text-slate-900 uppercase truncate max-w-[200px]">{file.name}</p>
                                                <p className="text-[10px] text-slate-500">
                                                    SIZE: {(file.size / 1024).toFixed(1)} KB | TYPE: VCF
                                                </p>
                                            </div>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); onFileChange(null); }}
                                                className="text-[10px] text-red-500 hover:text-red-700 font-mono underline decoration-dotted underline-offset-4 uppercase"
                                            >
                                                Remove file
                                            </button>
                                        </motion.div>
                                    ) : (
                                        <motion.div
                                            key="empty"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="space-y-3 pointer-events-none relative z-10"
                                        >
                                            <div className="w-12 h-12 border border-slate-300 text-slate-400 flex items-center justify-center mx-auto group-hover:bg-white transition-colors">
                                                <Upload className="w-6 h-6" />
                                            </div>
                                            <div className="font-mono text-xs">
                                                <p className="font-bold text-slate-700 uppercase">Drop your VCF file here</p>
                                                <p className="text-slate-400 mt-1">or click to browse</p>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>

                            {/* Format explicitly supported underneath */}
                            <div className="text-[10px] text-slate-400 text-center font-mono mt-2 tracking-wider">
                                SUPPORTS .VCF FILES UP TO 5MB
                            </div>
                        </div>

                        {/* Step 2 — Drug Selection */}
                        <div className="space-y-4">
                            <label className="text-xs font-bold text-slate-900 flex items-center justify-between font-mono uppercase">
                                <span>2. Select drugs to analyse</span>
                                <span className={cn("text-[10px] px-1.5 py-0.5 rounded", selectedDrugs.length > 0 ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-500")}>
                                    {selectedDrugs.length > 0 ? `${selectedDrugs.length} selected` : "Required"}
                                </span>
                            </label>

                            <div className="grid grid-cols-2 gap-2">
                                {supportedDrugs.map((drug, index) => {
                                    const isSelected = selectedDrugs.includes(drug);
                                    return (
                                        <motion.button
                                            key={drug}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.3 + index * 0.05 }}
                                            onClick={() => onDrugToggle(drug)}
                                            className={cn(
                                                "px-3 py-2 text-xs font-mono font-medium text-left flex items-center gap-2 border transition-all duration-200",
                                                isSelected
                                                    ? "bg-teal-600 border-teal-600 text-white"
                                                    : "bg-white border-slate-200 text-slate-600 hover:border-teal-400 hover:bg-teal-50"
                                            )}
                                        >
                                            <span className="opacity-80">{DRUG_ICONS[drug]}</span>
                                            {drug}
                                        </motion.button>
                                    )
                                })}
                            </div>

                            {/* Search */}
                            {cpicDrugs.length > 0 && (
                                <div ref={searchRef} className="relative font-mono text-xs" role="search">
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                                        <input
                                            type="text"
                                            value={searchQuery}
                                            onChange={(e) => {
                                                setSearchQuery(e.target.value);
                                                setShowDropdown(true);
                                            }}
                                            onFocus={() => setShowDropdown(true)}
                                            onBlur={handleBlur}
                                            placeholder="Search by drug or gene (e.g. warfarin, CYP2C9)"
                                            autoComplete="off"
                                            spellCheck={false}
                                            className="w-full pl-9 pr-9 py-2 bg-slate-50 border border-slate-200 focus:bg-white focus:border-teal-500 outline-none transition-colors placeholder:text-slate-400"
                                        />
                                        {searchQuery && (
                                            <button
                                                onClick={() => { setSearchQuery(""); setShowDropdown(false); }}
                                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                                            >
                                                <X className="w-3.5 h-3.5" />
                                            </button>
                                        )}
                                    </div>
                                    <AnimatePresence>
                                        {showDropdown && filteredCpicDrugs.length > 0 && (
                                            <motion.div
                                                initial={{ opacity: 0, y: -4 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -4 }}
                                                className="absolute z-50 w-full mt-1 bg-white border border-slate-300 shadow-xl max-h-48 overflow-y-auto"
                                            >
                                                {filteredCpicDrugs.map((drug) => {
                                                    const drugKey = drug.drugname.toUpperCase();
                                                    const isSelected = selectedDrugs.includes(drugKey);
                                                    return (
                                                        <button
                                                            key={drug.drugname}
                                                            onMouseDown={(e) => {
                                                                e.preventDefault();
                                                                onDrugToggle(drugKey);
                                                            }}
                                                            className={cn(
                                                                "w-full px-4 py-2 flex items-center justify-between text-left transition-colors border-b border-slate-100 last:border-0 hover:bg-slate-50",
                                                                isSelected && "bg-teal-50"
                                                            )}
                                                        >
                                                            <div className="flex-1">
                                                                <div className="font-bold text-xs text-slate-800">{drug.drugname}</div>
                                                                <div className="text-[10px] text-slate-400">{drug.genesymbol}</div>
                                                            </div>
                                                            {drug.supported && (
                                                                <span className="text-[9px] bg-emerald-100 text-emerald-700 px-1 py-0.5 border border-emerald-200">
                                                                    FULL
                                                                </span>
                                                            )}
                                                        </button>
                                                    );
                                                })}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            )}

                            {/* Selected pills */}
                            {selectedDrugs.filter(d => !supportedDrugs.includes(d)).length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                    {selectedDrugs.filter(d => !supportedDrugs.includes(d)).map(drug => (
                                        <div key={drug} className="flex items-center gap-1.5 px-2 py-1 bg-teal-50 border border-teal-200 text-[10px] font-mono font-medium text-teal-800">
                                            {drug}
                                            <button onClick={() => onDrugToggle(drug)} className="hover:text-red-500"><X className="w-3 h-3" /></button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Error */}
                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 text-xs font-mono text-red-600 flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                                <span className="uppercase">ERROR: {error}</span>
                            </div>
                        )}

                        {/* Action */}
                        <motion.button
                            onClick={onAnalyze}
                            disabled={!ready || loading}
                            className={cn(
                                "w-full py-4 text-sm font-bold font-mono tracking-widest uppercase flex items-center justify-center gap-3",
                                ready && !loading
                                    ? "bg-teal-500 text-white shadow-[0_0_20px_rgba(20,184,166,0.3)] border border-teal-400"
                                    : loading
                                        ? "bg-teal-600 text-white cursor-wait"
                                        : "bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed"
                            )}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Analysing&hellip;
                                </>
                            ) : (
                                <>
                                    <Cpu className="w-4 h-4" />
                                    Run analysis
                                    <ChevronRight className="w-4 h-4" />
                                </>
                            )}
                        </motion.button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
