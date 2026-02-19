import Link from "next/link";
import { Search } from "lucide-react";

export default function NotFound() {
    return (
        <div className="min-h-screen flex items-center justify-center px-6">
            <div className="text-center max-w-md space-y-6">
                <div
                    className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center"
                    style={{ background: "var(--surface-2, #f5f5f5)", color: "var(--text-secondary, #666)" }}
                >
                    <Search className="w-8 h-8" aria-hidden="true" />
                </div>
                <h2
                    className="text-2xl font-bold text-wrap-balance"
                    style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary, #111)" }}
                >
                    Page Not Found
                </h2>
                <p className="text-sm" style={{ color: "var(--text-secondary, #666)" }}>
                    The page you&apos;re looking for doesn&apos;t exist or has been moved.
                </p>
                <Link
                    href="/"
                    className="inline-block px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition-colors duration-200"
                    style={{ background: "var(--accent, #2563eb)" }}
                >
                    Back to PharmaGuard
                </Link>
            </div>
        </div>
    );
}
