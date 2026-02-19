"use client";

import { ExternalLink, BookOpen, Activity, Dna, FileText, Shield, ArrowRight, CornerDownRight } from "lucide-react";
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
        references: string[];
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
        <div className="bg-white/50 backdrop-blur-sm p-6 md:p-8 space-y-8 font-mono text-sm">

            {/* Exploded View Connector Lines */}
            <div className="grid md:grid-cols-12 gap-8">

                {/* ─── Col 1: Mechanism (Left) ─── */}
                <div className="md:col-span-8 space-y-6">

                    {/* Primary Action Box */}
                    <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="border-l-2 border-slate-900 pl-6 relative"
                    >
                        <div className="absolute -left-[5px] top-0 w-2 h-2 bg-slate-900 rounded-full"></div>
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                            Clinical_Directive
                        </h3>
                        <p className="text-lg text-slate-900 font-bold leading-relaxed">
                            {recommendation.action}
                        </p>
                        <p className="text-slate-600 mt-2 border-l border-slate-200 pl-4 py-1 italic">
                            "{recommendation.dosing_guidance}"
                        </p>
                    </motion.div>

                    {/* Alternatives */}
                    {recommendation.alternative_drugs.length > 0 && (
                        <div className="pl-6">
                            <h4 className="text-[10px] uppercase text-slate-400 mb-2 flex items-center gap-2">
                                <CornerDownRight className="w-3 h-3" /> Alternatives
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {recommendation.alternative_drugs.map(drug => (
                                    <span key={drug} className="px-2 py-1 bg-white border border-slate-300 text-slate-700 text-xs font-medium shadow-[2px_2px_0px_rgba(0,0,0,0.05)]">
                                        {drug}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="h-px bg-slate-200 w-full my-6 bg-[url('/dotted.svg')]"></div>

                    {/* Mechanism */}
                    <div className="grid md:grid-cols-2 gap-6 text-xs">
                        <div className="space-y-2">
                            <h4 className="font-bold text-slate-900 uppercase flex items-center gap-2">
                                <Activity className="w-3 h-3 text-teal-500" /> Mechanism
                            </h4>
                            <p className="text-slate-600 leading-relaxed text-justify">
                                {explanation.mechanism}
                            </p>
                        </div>
                        <div className="space-y-2">
                            <h4 className="font-bold text-slate-900 uppercase flex items-center gap-2">
                                <Shield className="w-3 h-3 text-teal-500" /> Guideline
                            </h4>
                            <p className="text-slate-600">
                                {cpicData?.guideline_name || "No specific guideline"}
                            </p>
                            <a href={guidelineUrl} target="_blank" className="inline-flex items-center gap-1 text-teal-600 hover:underline mt-1">
                                [ACCESS_SOURCE] <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* ─── Col 2: Genetics (Right sidebar) ─── */}
                <div className="md:col-span-4 border-t md:border-t-0 md:border-l border-slate-200 md:pl-8 pt-8 md:pt-0">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Dna className="w-4 h-4" /> Molecular_Profile
                    </h3>

                    <div className="space-y-4">
                        {variants.map((v, i) => (
                            <div key={i} className="bg-white border border-slate-200 p-3 shadow-sm relative group">
                                <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-slate-300"></div>
                                <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-slate-300"></div>

                                <div className="flex justify-between items-center mb-1">
                                    <span className="font-bold text-teal-700">{v.rsid}</span>
                                    <span className="text-[10px] bg-slate-100 px-1 rounded text-slate-500">{v.genotype}</span>
                                </div>
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-2">{v.gene}</div>
                                <div className="text-xs text-slate-700 font-medium leading-tight">
                                    {v.clinical_significance}
                                </div>
                            </div>
                        ))}

                        {variants.length === 0 && (
                            <div className="text-xs text-slate-400 italic p-4 border border-dashed border-slate-200 text-center">
                                No variants deteced in target region.
                            </div>
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
}
