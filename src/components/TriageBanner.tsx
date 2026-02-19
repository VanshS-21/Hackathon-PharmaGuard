"use client";

import { AlertTriangle, CheckCircle, HelpCircle, XCircle, Shield, BookOpen, Activity } from "lucide-react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface TriageBannerProps {
    riskLabel: string;
    drugName: string;
    gene: string;
    phenotype: string;
    cpicLevel?: string | null;
    dataSource?: string;
}

const LEVEL_COLORS: Record<string, string> = {
    A: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
    B: "bg-blue-500/10 text-blue-600 border-blue-500/20",
    C: "bg-amber-500/10 text-amber-600 border-amber-500/20",
    D: "bg-slate-500/10 text-slate-500 border-slate-500/20",
};

export function TriageBanner({
    riskLabel,
    drugName,
    gene,
    phenotype,
    cpicLevel,
    dataSource,
}: TriageBannerProps) {
    const label = riskLabel.toLowerCase();

    // Default: Unknown
    let containerClass = "bg-slate-50 border-slate-200";
    let accentClass = "text-slate-500";
    let icon = <HelpCircle className="w-6 h-6" />;
    let headline = "STATUS UNKNOWN";
    let statusId = "UNKNOWN";

    if (label.includes("safe") || label.includes("normal")) {
        containerClass = "bg-emerald-50/50 border-emerald-200";
        accentClass = "text-emerald-600";
        icon = <CheckCircle className="w-6 h-6" />;
        headline = "USE AS DIRECTED";
        statusId = "SAFE";
    } else if (label.includes("guideline")) {
        containerClass = "bg-sky-50/50 border-sky-200";
        accentClass = "text-sky-600";
        icon = <BookOpen className="w-6 h-6" />;
        headline = "GUIDELINE REQ.";
        statusId = "INFO";
    } else if (label.includes("adjust") || label.includes("monitor") || label.includes("intermediate")) {
        containerClass = "bg-amber-50/50 border-amber-200";
        accentClass = "text-amber-600";
        icon = <AlertTriangle className="w-6 h-6" />;
        headline = "ADJUST DOSAGE";
        statusId = "WARNING";
    } else if (label.includes("toxic") || label.includes("poor") || label.includes("risk")) {
        containerClass = "bg-red-50/50 border-red-200";
        accentClass = "text-red-600";
        icon = <XCircle className="w-6 h-6" />;
        headline = "CONTRAINDICATED";
        statusId = "CRITICAL";
    }

    const isCpic = dataSource === "CPIC API";
    const levelClass = cpicLevel ? (LEVEL_COLORS[cpicLevel] || LEVEL_COLORS.D) : "";

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className={cn(
                "relative overflow-hidden border-b p-6",
                containerClass
            )}
        >
            <div className="absolute top-0 right-0 p-2 opacity-10">
                <Activity className="w-32 h-32" />
            </div>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                <div className="flex items-start gap-4">
                    <div className={cn("p-3 rounded border bg-white/50 backdrop-blur-sm", accentClass, containerClass)}>
                        {icon}
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <div className={cn("text-[10px] font-mono font-bold uppercase tracking-widest px-1.5 py-0.5 rounded border", accentClass, "bg-white/50 border-current")}>
                                {statusId}
                            </div>
                            <span className="text-[10px] font-mono text-slate-400 uppercase">
                                REF: {drugName}
                            </span>
                        </div>
                        <h2 className={cn("text-2xl font-bold tracking-tight", accentClass)}>
                            {headline}
                        </h2>
                    </div>
                </div>

                <div className="flex items-center gap-8 font-mono text-xs">
                    <div>
                        <div className="text-slate-400 uppercase text-[10px] mb-1">Genotype</div>
                        <div className="font-bold text-slate-700 bg-white/50 px-2 py-1 rounded border border-slate-200">
                            {gene} <span className="text-slate-400">|</span> {phenotype}
                        </div>
                    </div>
                    {cpicLevel && (
                        <div>
                            <div className="text-slate-400 uppercase text-[10px] mb-1">Evidence</div>
                            <div className={cn("font-bold px-2 py-1 rounded border", levelClass)}>
                                LEVEL {cpicLevel}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}
