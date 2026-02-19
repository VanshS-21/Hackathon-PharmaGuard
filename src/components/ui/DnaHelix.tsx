"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

interface DnaHelixProps {
    /** Canvas width in px */
    width?: number;
    /** Canvas height in px */
    height?: number;
    /** Global alpha for the entire canvas draw (0–1) */
    opacity?: number;
    /** Rotation speed multiplier — 1 = ~20 s/full cycle */
    speed?: number;
    /** Tailwind / custom class names for positioning */
    className?: string;
    /** Primary strand colour (default teal) */
    strandColor?: string;
    /** Rung colour (default slate) */
    rungColor?: string;
}

export function DnaHelix({
    width = 160,
    height = 400,
    opacity = 0.12,
    speed = 1,
    className,
    strandColor = "20,184,166",   // teal-500
    rungColor = "148,163,184",    // slate-400
}: DnaHelixProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const rafRef = useRef<number>(0);
    const reducedMotion = useRef(false);

    useEffect(() => {
        if (typeof window === "undefined") return;

        // Respect prefers-reduced-motion
        const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
        reducedMotion.current = mq.matches;

        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Hi-DPI support
        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);

        let phase = 0;
        const AMPLITUDE = width * 0.28;   // how wide the helix sways
        const CX = width / 2;             // horizontal centre
        const NUCLEOTIDE_STEP = 18;       // px between base-pair rungs
        const STRAND_WIDTH = 2;
        const RUNG_WIDTH = 1;
        const NODE_RADIUS = 3;

        /**
         * Draw one frame of the helix.
         * @param t - accumulated phase offset in radians
         */
        const draw = (t: number) => {
            ctx.clearRect(0, 0, width, height);

            const steps = Math.ceil(height / NUCLEOTIDE_STEP) + 2;

            // ── draw rungs first (behind strands) ──────────────────────────
            for (let i = 0; i < steps; i++) {
                const y = i * NUCLEOTIDE_STEP - (t * NUCLEOTIDE_STEP * 2) % (NUCLEOTIDE_STEP * 2);
                const angle = (i / steps) * Math.PI * 4 + t;

                const x1 = CX + Math.sin(angle) * AMPLITUDE;
                const x2 = CX + Math.sin(angle + Math.PI) * AMPLITUDE;

                // depth cue: rungs behind look lighter
                const depthAlpha = (Math.sin(angle) + 1) / 2;
                const baseAlpha = 0.25 + depthAlpha * 0.55;

                ctx.beginPath();
                ctx.moveTo(x1, y);
                ctx.lineTo(x2, y);
                ctx.strokeStyle = `rgba(${rungColor},${baseAlpha * opacity * 6})`;
                ctx.lineWidth = RUNG_WIDTH;
                ctx.stroke();
            }

            // ── draw strand A (sin) ─────────────────────────────────────────
            const drawStrand = (phaseOffset: number) => {
                ctx.beginPath();
                for (let y = -2; y <= height + 2; y += 2) {
                    const angle = (y / height) * Math.PI * 4 + t;
                    const x = CX + Math.sin(angle + phaseOffset) * AMPLITUDE;
                    if (y === -2) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = `rgba(${strandColor},${opacity * 5.5})`;
                ctx.lineWidth = STRAND_WIDTH;
                ctx.stroke();
            };

            drawStrand(0);
            drawStrand(Math.PI);

            // ── draw nucleotide nodes ───────────────────────────────────────
            for (let i = 0; i < steps; i++) {
                const y = i * NUCLEOTIDE_STEP - (t * NUCLEOTIDE_STEP * 2) % (NUCLEOTIDE_STEP * 2);
                const angle = (i / steps) * Math.PI * 4 + t;

                [[0, strandColor], [Math.PI, strandColor]].forEach(([offset, color]) => {
                    const x = CX + Math.sin((angle as number) + (offset as number)) * AMPLITUDE;
                    const depth = (Math.sin((angle as number) + (offset as number)) + 1) / 2;
                    const nodeAlpha = 0.3 + depth * 0.7;
                    const r = NODE_RADIUS * (0.6 + depth * 0.4);

                    ctx.beginPath();
                    ctx.arc(x, y, r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(${color},${nodeAlpha * opacity * 6})`;
                    ctx.fill();
                });
            }
        };

        if (reducedMotion.current) {
            // Static single frame
            draw(0.4);
            return;
        }

        // Animated loop
        const BASE_SPEED = 0.0003;
        let lastTime = 0;

        const loop = (timestamp: number) => {
            const delta = timestamp - lastTime;
            lastTime = timestamp;
            phase += delta * BASE_SPEED * speed;
            draw(phase);
            rafRef.current = requestAnimationFrame(loop);
        };

        rafRef.current = requestAnimationFrame(loop);

        return () => {
            cancelAnimationFrame(rafRef.current);
        };
    }, [width, height, opacity, speed, strandColor, rungColor]);

    return (
        <canvas
            ref={canvasRef}
            style={{ width, height }}
            className={cn("pointer-events-none select-none", className)}
            aria-hidden="true"
        />
    );
}
