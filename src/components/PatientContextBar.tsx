"use client";

import { User, X, Calendar } from "lucide-react";
import { motion } from "motion/react";

interface PatientContextBarProps {
    patientId: string;
    patientName?: string;
    patientDob?: string;
    onClear: () => void;
}

export function PatientContextBar({
    patientId,
    patientName,
    patientDob,
    onClear,
}: PatientContextBarProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="sticky top-16 z-40 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 shadow-sm"
        >
            <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2.5">
                        <div className="w-6 h-6 bg-teal-600 rounded-md flex items-center justify-center text-white text-[10px] font-black tracking-tighter">
                            PGx
                        </div>
                        <span className="font-bold text-slate-900 text-sm tracking-tight">Pharmacogenomics Report</span>
                    </div>

                    <div className="h-4 w-px bg-slate-300 hidden md:block" />

                    <div className="hidden md:flex items-center gap-6 text-sm">
                        {patientName && (
                            <div className="flex items-center gap-2">
                                <User className="w-4 h-4 text-slate-400" />
                                <span className="font-semibold text-slate-900">{patientName}</span>
                            </div>
                        )}
                        <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-slate-400" />
                            <span className="text-slate-500">Patient ID:</span>
                            <span className="font-mono font-semibold text-slate-900">{patientId}</span>
                        </div>
                        {patientDob && (
                            <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-slate-400" />
                                <span className="text-slate-500">DOB:</span>
                                <span className="font-mono font-medium text-slate-700">{patientDob}</span>
                            </div>
                        )}
                    </div>
                </div>

                <button
                    onClick={onClear}
                    className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                >
                    <X className="w-3.5 h-3.5" />
                    New analysis
                </button>
            </div>
        </motion.div>
    );
}
