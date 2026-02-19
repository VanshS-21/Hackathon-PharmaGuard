"use client";

import { AlertTriangle, CheckCircle, HelpCircle, XCircle } from "lucide-react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface TriageBannerProps {
    riskLabel: string;
    drugName: string;
    gene: string;
    phenotype: string;
}

export function TriageBanner({
    riskLabel,
    drugName,
    gene,
    phenotype,
}: TriageBannerProps) {
    const label = riskLabel.toLowerCase();

    // Default: Unknown
    let containerClass = "bg-slate-50 border-slate-200";
    let accentClass = "text-slate-500";
    let icon = <HelpCircle className="w-8 h-8" />;
    let headline = "STATUS UNKNOWN";
    let borderClass = "border-l-slate-400";

    if (label.includes("safe") || label.includes("normal")) {
        containerClass = "bg-emerald-50 border-emerald-100";
        accentClass = "text-emerald-700";
        borderClass = "border-l-emerald-600";
        icon = <CheckCircle className="w-8 h-8" />;
        headline = "USE AS DIRECTED";
    } else if (label.includes("adjust") || label.includes("monitor") || label.includes("intermediate")) {
        containerClass = "bg-amber-50 border-amber-100";
        accentClass = "text-amber-700";
        borderClass = "border-l-amber-600";
        icon = <AlertTriangle className="w-8 h-8" />;
        headline = "CAUTION — ADJUST DOSAGE";
    } else if (label.includes("toxic") || label.includes("poor") || label.includes("risk")) {
        containerClass = "bg-red-50 border-red-100";
        accentClass = "text-red-700";
        borderClass = "border-l-red-600";
        icon = <XCircle className="w-8 h-8" />;
        headline = "HIGH RISK — DO NOT PRESCRIBE";
    }

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className={cn(
                "w-full flex flex-col md:flex-row items-start md:items-center gap-6 relative overflow-hidden border-y md:border md:rounded-t-xl p-6 md:p-8",
                containerClass,
                "border-l-4 md:border-l-4", // Thick left border for medical alert style
                borderClass
            )}
        >
            {/* Icon */}
            <div className={cn("flex-shrink-0", accentClass)}>
                {icon}
            </div>

            {/* Main Alert Text */}
            <div className="flex-grow space-y-1">
                <div className={cn("text-xs font-bold uppercase tracking-widest opacity-80", accentClass)}>
                    {drugName} Risk Assessment
                </div>
                <h2 className={cn("text-2xl md:text-3xl font-bold tracking-tight", accentClass)}>
                    {headline}
                </h2>
            </div>

            {/* Phenotype Context */}
            <div className="hidden md:block pl-6 border-l border-black/5 min-w-[180px]">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                    Genotype
                </div>
                <div className="font-bold text-lg text-slate-900 leading-none mb-1">
                    {gene}
                </div>
                <div className="text-sm font-medium text-slate-600">
                    {phenotype}
                </div>
            </div>
        </motion.div>
    );
}
