"use client";

import { useEffect } from "react";

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error("Application error:", error);
    }, [error]);

    return (
        <div className="min-h-screen flex items-center justify-center px-6">
            <div className="text-center max-w-md space-y-6">
                <div
                    className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-2xl"
                    style={{ background: "var(--danger-bg, #fef2f2)", color: "var(--danger, #dc2626)" }}
                >
                    ⚠️
                </div>
                <h2
                    className="text-2xl font-bold"
                    style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary, #111)" }}
                >
                    Something went wrong
                </h2>
                <p className="text-sm" style={{ color: "var(--text-secondary, #666)" }}>
                    An unexpected error occurred. Please try again or contact support if the problem persists.
                </p>
                <button
                    onClick={reset}
                    className="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors"
                    style={{ background: "var(--accent, #2563eb)" }}
                >
                    Try Again
                </button>
            </div>
        </div>
    );
}
