"use client";

import { motion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { Loader2, Check, FlaskConical, Dna, FileSearch, Terminal, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProcessingStateProps {
    onComplete: () => void;
}

const STEPS = [
    { id: 1, label: "PARSING_GENOMIC_DATA", icon: FileSearch, duration: 800, details: "Extracting variants..." },
    { id: 2, label: "IDENTIFYING_PHARMACOGENES", icon: Dna, duration: 1200, details: "Matching CYP450..." },
    { id: 3, label: "ANALYZING_INTERACTIONS", icon: FlaskConical, duration: 1500, details: "Cross-referencing..." },
    { id: 4, label: "GENERATING_REPORT", icon: Terminal, duration: 800, details: "Compiling JSON..." },
];

export function ProcessingState({ onComplete }: ProcessingStateProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const hasRun = useRef(false);
    const onCompleteRef = useRef(onComplete);
    // Keep ref in sync without re-running the effect
    onCompleteRef.current = onComplete;

    useEffect(() => {
        if (hasRun.current) return;
        hasRun.current = true;

        const runSteps = async () => {
            for (let i = 0; i < STEPS.length; i++) {
                setCurrentStep(i);
                await new Promise((resolve) => setTimeout(resolve, STEPS[i].duration));
            }
            onCompleteRef.current();
        };

        runSteps();
    }, []); // empty dep array — intentional, guarded by hasRun ref

    return (
        <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 max-w-lg mx-auto w-full">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full panel-tech p-6 space-y-6 bg-slate-900 border-slate-700 text-slate-100"
            >
                <div className="flex items-center justify-between border-b border-slate-700 pb-4">
                    <div className="flex items-center gap-2 text-teal-400 font-mono text-xs uppercase tracking-widest">
                        <Activity className="w-4 h-4 animate-pulse" />
                        System_Diagnostics
                    </div>
                    <div className="font-mono text-[10px] text-slate-500">
                        PID: {Math.floor(Math.random() * 99999)}
                    </div>
                </div>

                <div className="space-y-1">
                    {STEPS.map((step, index) => {
                        const isActive = index === currentStep;
                        const isCompleted = index < currentStep;

                        return (
                            <div
                                key={step.id}
                                className={cn(
                                    "flex items-center gap-4 p-3 font-mono text-sm border-l-2 transition-all duration-300",
                                    isActive ? "border-teal-500 bg-teal-500/10 text-teal-300" :
                                        isCompleted ? "border-emerald-500 text-emerald-400 opacity-50" :
                                            "border-slate-700 text-slate-600"
                                )}
                            >
                                <div className="w-5 h-5 flex items-center justify-center">
                                    {isCompleted ? <Check className="w-4 h-4" /> :
                                        isActive ? <Loader2 className="w-4 h-4 animate-spin" /> :
                                            <step.icon className="w-4 h-4" />}
                                </div>
                                <div className="flex-1">
                                    <div className="font-bold tracking-wider">{step.label}</div>
                                    {isActive && (
                                        <div className="text-[10px] text-teal-500/80 mt-1 uppercase typing-effect">
                                            {">"} {step.details}
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className="border-t border-slate-700 pt-4">
                    <div className="w-full bg-slate-800 h-1 mt-2">
                        <motion.div
                            className="h-full bg-teal-500 shadow-[0_0_10px_rgba(20,184,166,0.5)]"
                            initial={{ width: "0%" }}
                            animate={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
                            transition={{ type: "spring", stiffness: 80, damping: 20 }}
                        />
                    </div>
                    <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2 uppercase">
                        <span>Progress</span>
                        <span>{Math.round(((currentStep + 1) / STEPS.length) * 100)}%</span>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
