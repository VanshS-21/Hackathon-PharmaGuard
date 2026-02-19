"use client";

import { ExternalLink, BookOpen, Activity, Dna, FileText, Shield } from "lucide-react";
import { motion } from "motion/react";

interface DetectedVariant {
    rsid: string;
    gene: string;
    genotype: string;
    clinical_significance: string;
}

interface CpicData {
    recommendation: string | null;
    classification: string | null;
    evidence_level: string | null;
    guideline_name: string | null;
    guideline_url: string | null;
    implications: Record<string, string> | null;
    data_source: string;
}

interface ActionPanelProps {
    recommendation: {
        action: string;
        dosing_guidance: string;
        alternative_drugs: string[];
        monitoring: string;
    };
    explanation: {
        mechanism: string;
        evidence_level: string;
    };
    variants: DetectedVariant[];
    cpicData?: CpicData | null;
}

export function ActionPanel({
    recommendation,
    explanation,
    variants,
    cpicData,
}: ActionPanelProps) {
    const isCpic = cpicData?.data_source === "CPIC API";
    const guidelineUrl = cpicData?.guideline_url || "#";

    return (
        <div className="bg-white border-x border-b border-slate-200 rounded-b-xl p-6 md:p-8 space-y-8">
            <div className="grid md:grid-cols-3 gap-8">

                {/* ─── Col 1: Action (Primary) ─── */}
                <div className="md:col-span-2 space-y-8">
                    {/* Clinical Action Box */}
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 }}
                        className="bg-slate-50 rounded-xl border border-slate-200 p-6 shadow-sm"
                    >
                        <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-teal-600" />
                            Clinical Recommendation
                        </h3>

                        <p className="text-base text-slate-700 leading-relaxed mb-6">
                            <strong className="text-slate-900">{recommendation.action}:</strong>{" "}
                            {recommendation.dosing_guidance}
                        </p>

                        {recommendation.alternative_drugs.length > 0 && (
                            <div className="flex flex-wrap items-center gap-3">
                                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                                    Alternatives:
                                </span>
                                {recommendation.alternative_drugs.map((drug) => (
                                    <span
                                        key={drug}
                                        className="text-xs font-semibold px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-700 shadow-sm"
                                    >
                                        {drug}
                                    </span>
                                ))}
                            </div>
                        )}
                    </motion.div>

                    {/* CPIC Official Recommendation */}
                    {isCpic && cpicData?.recommendation && (
                        <motion.div
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.22 }}
                            className="bg-teal-50 rounded-xl border border-teal-200 p-6 shadow-sm"
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="flex items-center gap-1.5 text-teal-700">
                                    <Shield className="w-5 h-5" />
                                    <h3 className="text-base font-bold">CPIC Official Recommendation</h3>
                                </div>
                                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-700 border border-teal-200">
                                    CPIC Verified
                                </span>
                            </div>

                            <p className="text-sm text-teal-900 leading-relaxed mb-4">
                                {cpicData.recommendation}
                            </p>

                            {cpicData.guideline_name && (
                                <div className="flex items-center gap-4 pt-2 border-t border-teal-200/50">
                                    <span className="text-xs text-teal-600 font-medium truncate flex-1">
                                        {cpicData.guideline_name}
                                    </span>
                                    {cpicData.classification && (
                                        <span className="text-xs font-bold px-2 py-0.5 rounded bg-teal-100 text-teal-800">
                                            {cpicData.classification}
                                        </span>
                                    )}
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Evidence Section */}
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="space-y-4"
                    >
                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            Evidence & Mechanism
                        </h4>

                        <div className="grid sm:grid-cols-2 gap-4">
                            <div className="bg-white p-4 rounded-lg border border-slate-100">
                                <span className="block text-xs font-semibold text-slate-400 mb-1">Mechanism</span>
                                <p className="text-sm text-slate-700 leading-relaxed">
                                    {explanation.mechanism}
                                </p>
                            </div>
                            <div className="bg-white p-4 rounded-lg border border-slate-100">
                                <span className="block text-xs font-semibold text-slate-400 mb-1">Monitoring</span>
                                <p className="text-sm text-slate-700 leading-relaxed">
                                    {recommendation.monitoring}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-6 pt-2">
                            <a
                                href={guidelineUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-xs font-medium text-teal-600 hover:text-teal-700 hover:underline"
                            >
                                <BookOpen className="w-3.5 h-3.5" /> CPIC Guidelines
                            </a>
                            <a href="#" className="flex items-center gap-2 text-xs font-medium text-teal-600 hover:text-teal-700 hover:underline">
                                <ExternalLink className="w-3.5 h-3.5" /> PharmGKB Reference
                            </a>
                            <span className="ml-auto text-xs font-mono text-slate-400 bg-slate-50 px-2 py-1 rounded">
                                Level {explanation.evidence_level} Evidence
                            </span>
                        </div>
                    </motion.div>
                </div>

                {/* ─── Col 2: Genetics ─── */}
                <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="md:col-span-1"
                >
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden h-full">
                        <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest">
                            <Dna className="w-3.5 h-3.5" />
                            Genomic Markers
                        </div>

                        <div className="divide-y divide-slate-100">
                            {variants.length > 0 ? (
                                variants.map((v, i) => (
                                    <div key={i} className="p-4 hover:bg-slate-50 transition-colors">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="font-mono font-bold text-sm text-teal-700">{v.rsid}</span>
                                            <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
                                                {v.genotype}
                                            </span>
                                        </div>
                                        <div className="text-xs text-slate-500 mb-1">Gene: {v.gene}</div>
                                        <div className="text-xs font-medium text-slate-700">
                                            {v.clinical_significance}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="p-6 text-center text-sm text-slate-400 italic">
                                    No variants found in target panel.
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}

