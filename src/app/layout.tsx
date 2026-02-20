import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Activity, Shield, Terminal, Zap } from "lucide-react";
import "./globals.css";

// ─── Fonts ───
const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

const SITE_URL = process.env.NEXT_PUBLIC_APP_URL || "https://hackathon-pharma-guard.vercel.app";

export const metadata: Metadata = {
  title: "PharmaGuard | Pharmacogenomic Risk Prediction",
  description: "PharmaGuard analyzes patient VCF genetic data to predict personalized drug risks and provide CPIC Level A clinically actionable recommendations for safer prescribing decisions.",
  metadataBase: new URL(SITE_URL),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "PharmaGuard | Pharmacogenomic Risk Prediction",
    description: "AI-powered pharmacogenomics: upload a VCF file and instantly get CPIC-aligned drug risk predictions for safer prescribing.",
    url: SITE_URL,
    siteName: "PharmaGuard",
    type: "website",
    images: [
      {
        url: `${SITE_URL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "PharmaGuard - Pharmacogenomic Risk Prediction",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "PharmaGuard | Pharmacogenomic Risk Prediction",
    description: "Upload a VCF file and get CPIC Level A drug risk predictions in seconds.",
    images: [`${SITE_URL}/og-image.png`],
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased text-slate-900 bg-slate-50 selection:bg-teal-500/30 selection:text-teal-900">

        {/* ─── SYSTEM CHROME ─── */}
        <div className="fixed top-0 left-0 right-0 z-50 h-10 bg-slate-900 border-b border-slate-700 flex items-center justify-between px-4 text-[10px] font-mono text-slate-400 uppercase tracking-wider backdrop-blur-md bg-opacity-90">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-slate-100 font-bold">
              <Shield className="w-3.5 h-3.5 text-teal-500" />
              PharmaGuard <span className="text-teal-500">v2.4.0</span>
            </div>
            <div className="hidden md:flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              Online
            </div>
            <div className="hidden md:flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-slate-600" />
              CPIC Level A
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:block">
              End-to-end encrypted
            </div>
            <div className="flex items-center gap-2 text-teal-500">
              <Zap className="w-3.5 h-3.5 text-yellow-500" />
              Secure session
            </div>
            <div className="pl-6 border-l border-slate-700 text-slate-300">
              {new Date().toISOString().split('T')[0]}
            </div>
          </div>
        </div>

        {/* ─── CORNER MARKERS (HUD) ─── */}
        <div className="fixed top-12 left-4 w-4 h-4 border-t-2 border-l-2 border-slate-300 pointer-events-none z-40 opacity-50"></div>
        <div className="fixed top-12 right-4 w-4 h-4 border-t-2 border-r-2 border-slate-300 pointer-events-none z-40 opacity-50"></div>
        <div className="fixed bottom-4 left-4 w-4 h-4 border-b-2 border-l-2 border-slate-300 pointer-events-none z-40 opacity-50"></div>
        <div className="fixed bottom-4 right-4 w-4 h-4 border-b-2 border-r-2 border-slate-300 pointer-events-none z-40 opacity-50"></div>

        {/* ─── SKIP LINK (accessibility) ─── */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-12 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-teal-600 focus:text-white focus:rounded text-sm font-medium"
        >
          Skip to main content
        </a>

        {/* ─── MAIN CONTENT ─── */}
        <main id="main-content" className="pt-16 min-h-screen relative z-10">
          {children}
        </main>

        {/* ─── FOOTER ─── */}
        <footer className="border-t border-slate-200 bg-white/50 backdrop-blur-sm mt-auto relative z-10">
          <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-mono text-slate-500 uppercase tracking-wide">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4" />
              <span>PharmaGuard Clinical Systems &copy; 2026</span>
            </div>
            <div className="flex gap-6">
              <a href="#" className="hover:text-teal-600 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-teal-600 transition-colors">Terms of Use</a>
              <a href="#" className="hover:text-teal-600 transition-colors">System Status</a>
            </div>
          </div>
        </footer>

      </body>
    </html>
  );
}
