"use client";

import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Loader2, CheckCircle2, FlaskConical, Dna, FileSearch } from "lucide-react";

interface ProcessingStateProps {
    onComplete: () => void;
}

const STEPS = [
    { id: 1, label: "Parsing Genomic Data (VCF)", icon: FileSearch, duration: 800 },
    { id: 2, label: "Identifying Pharmacogenes", icon: Dna, duration: 1200 },
    { id: 3, label: "Analyzing Drug-Gene Interactions", icon: FlaskConical, duration: 1500 },
    { id: 4, label: "Generating Clinical Report", icon: CheckCircle2, duration: 800 },
];

export function ProcessingState({ onComplete }: ProcessingStateProps) {
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        const runSteps = async () => {
            for (let i = 0; i < STEPS.length; i++) {
                setCurrentStep(i);
                await new Promise((resolve) => setTimeout(resolve, STEPS[i].duration));
            }
            onComplete();
        };

        runSteps();
    }, [onComplete]);

    return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 max-w-lg mx-auto w-full">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full bg-white rounded-2xl border border-slate-200 shadow-xl p-8 space-y-8"
            >
                <div className="text-center space-y-2">
                    <div className="w-16 h-16 bg-teal-50 text-teal-600 rounded-full flex items-center justify-center mx-auto mb-4 border border-teal-100">
                        <Loader2 className="w-8 h-8 animate-spin" />
                    </div>
                    <h2 className="text-xl font-bold text-slate-900">Analyzing Patient Data</h2>
                    <p className="text-slate-500 text-sm">Please wait while the system processes the VCF file against CPIC guidelines.</p>
                </div>

                <div className="space-y-4">
                    {STEPS.map((step, index) => {
                        const isActive = index === currentStep;
                        const isCompleted = index < currentStep;
                        const isPending = index > currentStep;

                        return (
                            <motion.div
                                key={step.id}
                                initial={{ x: -10, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: index * 0.1 }}
                                className={`flex items-center gap-4 p-3 rounded-lg transition-colors ${isActive ? "bg-slate-50 border border-slate-100" : "transparent"
                                    }`}
                            >
                                <div
                                    className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 ${isCompleted
                                            ? "bg-emerald-500 border-emerald-500 text-white"
                                            : isActive
                                                ? "bg-teal-50 border-teal-500 text-teal-600"
                                                : "bg-slate-100 border-slate-200 text-slate-300"
                                        }`}
                                >
                                    {isCompleted ? (
                                        <CheckCircle2 className="w-5 h-5" />
                                    ) : (
                                        <step.icon className={`w-4 h-4 ${isActive ? "animate-pulse" : ""}`} />
                                    )}
                                </div>
                                <div className="flex-1">
                                    <p
                                        className={`text-sm font-medium ${isPending ? "text-slate-400" : "text-slate-700"
                                            }`}
                                    >
                                        {step.label}
                                    </p>
                                </div>
                                {isActive && (
                                    <div className="w-4 h-4">
                                        <span className="relative flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-teal-500"></span>
                                        </span>
                                    </div>
                                )}
                            </motion.div>
                        );
                    })}
                </div>

                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-6">
                    <motion.div
                        className="h-full bg-teal-500"
                        initial={{ width: "0%" }}
                        animate={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>
            </motion.div>

            <p className="mt-8 text-xs text-slate-400 text-center max-w-sm">
                HIPAA Compliance: Data is processed locally in the browser context where possible and transiently on secure servers for analysis.
            </p>
        </div>
    );
}
