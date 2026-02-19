export const TOKENS = {
    colors: {
        // Clinical / Technical Base
        background: '#f8fafc', // Slate-50
        foreground: '#0f172a', // Slate-900

        // Blueprint Accents
        grid: 'rgba(148, 163, 184, 0.15)', // Slate-400 at 15%
        gridStrong: 'rgba(148, 163, 184, 0.4)',

        // Semantic Risks
        risk: {
            safe: '#059669',    // Emerald-600
            warning: '#d97706', // Amber-600
            danger: '#dc2626',  // Red-600
            neutral: '#475569', // Slate-600
        },

        // UI Chrome
        border: '#e2e8f0',       // Slate-200
        borderStrong: '#94a3b8', // Slate-400
    },

    layout: {
        gridSize: '40px',
        containerWidth: '1280px',
    },

    typography: {
        mono: '"JetBrains Mono", monospace',
        sans: '"Inter", system-ui, sans-serif',
    },

    animation: {
        scan: {
            duration: 2.0,
            ease: "easeInOut",
        }
    }
} as const;
