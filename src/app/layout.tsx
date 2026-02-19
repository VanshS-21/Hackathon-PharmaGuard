import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google"; // More clinical/professional
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-heading",
  subsets: ["latin"],
  weight: ["500", "600", "700", "800"],
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "PharmaGuard | Clinical Pharmacogenomics",
  description:
    "Professional pharmacogenomic risk prediction system. AI-powered analysis of VCF data for personalized clinical recommendations.",
  keywords: [
    "pharmacogenomics",
    "drug safety",
    "precision medicine",
    "clinical decision support",
  ],
  openGraph: {
    title: "PharmaGuard | Clinical Pharmacogenomics",
    description:
      "AI-powered pharmacogenomic risk prediction. Upload VCF data, select drugs, and get CPIC-backed clinical recommendations.",
    type: "website",
    locale: "en_US",
    siteName: "PharmaGuard",
  },
  twitter: {
    card: "summary_large_image",
    title: "PharmaGuard | Clinical Pharmacogenomics",
    description:
      "AI-powered pharmacogenomic risk prediction for precision medicine.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${jakarta.variable} ${inter.variable} antialiased`}
        style={{
          background: "var(--background)",
          color: "var(--foreground)"
        }}
      >
        {/* ─── Navbar ─── */}
        <nav
          className="fixed top-0 left-0 right-0 z-50 h-16 px-6 md:px-12 flex items-center justify-between"
          style={{
            background: "rgba(255, 255, 255, 0.8)",
            backdropFilter: "blur(12px)",
            WebkitBackdropFilter: "blur(12px)",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <div className="flex items-center gap-3">
            {/* Logo Mark - Clean Science */}
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold tracking-tight"
              style={{
                background: "var(--accent)",
                color: "white",
              }}
            >
              PG
            </div>
            <span
              className="text-lg font-bold tracking-tight"
              style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}
            >
              Pharma<span style={{ color: "var(--accent)" }}>Guard</span>
            </span>
          </div>

          {/* Status pill */}
          <div
            className="hidden md:flex items-center gap-2 text-xs font-semibold tracking-wider uppercase"
            style={{
              color: "var(--text-secondary)",
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              padding: "6px 14px",
              borderRadius: "9999px",
            }}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{
                background: "var(--safe)",
              }}
            />
            Research Protocol v2.4
          </div>
        </nav>

        {/* ─── Main Content ─── */}
        <main className="pt-16 min-h-screen">
          {children}
        </main>

        {/* ─── Footer ─── */}
        <footer
          className="py-12 border-t"
          style={{
            borderColor: "var(--border)",
            background: "var(--surface-0)",
          }}
        >
          <div className="max-w-6xl mx-auto px-6 text-center md:text-left flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-sm">
              <p className="font-semibold text-gray-900">PharmaGuard Clinical Systems</p>
              <p className="text-gray-500 mt-1">Precision Medicine for the Modern Clinic.</p>
            </div>
            <p className="text-xs text-gray-400">
              For Research Use Only. Not for diagnostic procedures without validation.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}

