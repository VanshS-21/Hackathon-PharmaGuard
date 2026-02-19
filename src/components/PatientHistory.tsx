"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { X, Clock, Pill, Trash2, ChevronRight } from "lucide-react";

export interface HistoryEntry {
    id: string;
    patientName: string;
    patientDob: string;
    timestamp: string;
    drugsAnalysed: string[];
    results: unknown[];
}

interface PatientHistoryProps {
    open: boolean;
    onClose: () => void;
    onLoad: (entry: HistoryEntry) => void;
}

export function PatientHistory({ open, onClose, onLoad }: PatientHistoryProps) {
    const [entries, setEntries] = useState<HistoryEntry[]>([]);

    useEffect(() => {
        if (open) {
            try {
                const raw = localStorage.getItem("pharmaguard-history");
                setEntries(raw ? JSON.parse(raw) : []);
            } catch {
                setEntries([]);
            }
        }
    }, [open]);

    const handleClearAll = () => {
        localStorage.removeItem("pharmaguard-history");
        setEntries([]);
    };

    const handleDelete = (id: string) => {
        const updated = entries.filter((e) => e.id !== id);
        localStorage.setItem("pharmaguard-history", JSON.stringify(updated));
        setEntries(updated);
    };

    return (
        <AnimatePresence>
            {open && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
                    />

                    {/* Drawer */}
                    <motion.div
                        initial={{ x: "100%" }}
                        animate={{ x: 0 }}
                        exit={{ x: "100%" }}
                        transition={{ type: "spring", damping: 30, stiffness: 300 }}
                        className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
                            <div className="flex items-center gap-3">
                                <Clock className="w-5 h-5 text-teal-600" />
                                <h2 className="text-lg font-bold text-slate-900">Patient History</h2>
                            </div>
                            <div className="flex items-center gap-2">
                                {entries.length > 0 && (
                                    <button
                                        onClick={handleClearAll}
                                        className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1 px-2 py-1 rounded hover:bg-red-50 transition-colors"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                        Clear all
                                    </button>
                                )}
                                <button
                                    onClick={onClose}
                                    className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
                                >
                                    <X className="w-4 h-4 text-slate-500" />
                                </button>
                            </div>
                        </div>

                        {/* Entries */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-3">
                            {entries.length === 0 ? (
                                <div className="text-center py-16 space-y-3">
                                    <Clock className="w-10 h-10 text-slate-300 mx-auto" />
                                    <p className="text-sm text-slate-500">No analyses yet</p>
                                    <p className="text-xs text-slate-400">
                                        Your completed analyses will appear here
                                    </p>
                                </div>
                            ) : (
                                entries.map((entry) => {
                                    const date = new Date(entry.timestamp);
                                    return (
                                        <motion.div
                                            key={entry.id}
                                            initial={{ opacity: 0, y: 8 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="group border border-slate-200 rounded-lg p-4 hover:border-teal-300 hover:bg-teal-50/30 transition-all cursor-pointer"
                                            onClick={() => onLoad(entry)}
                                        >
                                            <div className="flex items-start justify-between">
                                                <div className="space-y-1 flex-1 min-w-0">
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-sm text-slate-900 truncate">
                                                            {entry.patientName}
                                                        </span>
                                                        {entry.patientDob && (
                                                            <span className="text-[10px] text-slate-400 font-mono">
                                                                DOB: {entry.patientDob}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <div className="flex items-center gap-2 text-xs text-slate-500">
                                                        <Clock className="w-3 h-3" />
                                                        {date.toLocaleDateString()} at {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                                    </div>
                                                    <div className="flex flex-wrap gap-1 mt-2">
                                                        {entry.drugsAnalysed.map((drug) => (
                                                            <span
                                                                key={drug}
                                                                className="inline-flex items-center gap-1 text-[10px] font-mono font-medium px-2 py-0.5 bg-slate-100 text-slate-600 rounded"
                                                            >
                                                                <Pill className="w-2.5 h-2.5" />
                                                                {drug}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-1 ml-2">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleDelete(entry.id);
                                                        }}
                                                        className="w-7 h-7 flex items-center justify-center rounded text-slate-400 hover:text-red-500 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-all"
                                                    >
                                                        <Trash2 className="w-3.5 h-3.5" />
                                                    </button>
                                                    <ChevronRight className="w-4 h-4 text-teal-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })
                            )}
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
