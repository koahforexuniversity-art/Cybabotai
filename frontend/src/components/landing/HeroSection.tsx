"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { Bot, ArrowRight, Zap, Play, ChevronDown } from "lucide-react";
import { AGENT_CONFIGS } from "@/types/agent";

const TYPEWRITER_STRINGS = [
  "EURUSD scalping strategy with RSI + EMA crossover",
  "Gold breakout system using ATR-based stops",
  "GBPUSD mean reversion with Bollinger Bands",
  "Multi-timeframe trend following on JPY pairs",
];

export function HeroSection() {
  const [typewriterIndex, setTypewriterIndex] = useState(0);
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const heroRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(heroRef, { once: true });

  // Typewriter effect
  useEffect(() => {
    const current = TYPEWRITER_STRINGS[typewriterIndex];
    const timeout = setTimeout(
      () => {
        if (!isDeleting) {
          if (displayText.length < current.length) {
            setDisplayText(current.slice(0, displayText.length + 1));
          } else {
            setTimeout(() => setIsDeleting(true), 2000);
          }
        } else {
          if (displayText.length > 0) {
            setDisplayText(displayText.slice(0, -1));
          } else {
            setIsDeleting(false);
            setTypewriterIndex((i) => (i + 1) % TYPEWRITER_STRINGS.length);
          }
        }
      },
      isDeleting ? 30 : 60
    );
    return () => clearTimeout(timeout);
  }, [displayText, isDeleting, typewriterIndex]);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-4 pt-16"
    >
      {/* Background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyber-500 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.1, 0.6, 0.1],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}
      </div>

      {/* Hero content */}
      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.1 }}
          className="inline-flex items-center gap-2 badge-cyber px-4 py-1.5 rounded-full mb-8"
        >
          <span className="w-2 h-2 bg-cyber-400 rounded-full animate-pulse" />
          Cybabot Ultra — 7-Agent AI Crew
          <span className="text-cyber-400">•</span>
          <span>Open Source</span>
        </motion.div>

        {/* Main headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.2 }}
          className="text-5xl sm:text-6xl md:text-7xl font-black text-white mb-6 leading-tight tracking-tight"
        >
          Build{" "}
          <span className="gradient-text-cyber">Production-Ready</span>
          <br />
          Forex Bots with AI
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.3 }}
          className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          Describe your strategy in plain English. Cybabot's 7 specialized AI
          agents handle everything — from hypothesis to backtested, export-ready
          MQL5 EA in minutes.
        </motion.p>

        {/* Typewriter demo input */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ delay: 0.4 }}
          className="relative max-w-2xl mx-auto mb-10"
        >
          <div className="glass-card p-4 text-left">
            <div className="flex items-center gap-2 mb-2">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/60" />
              </div>
              <span className="text-xs text-muted-foreground font-mono">
                cybabot ~ strategy_builder
              </span>
            </div>
            <div className="font-mono text-sm">
              <span className="text-cyber-400">{">"} </span>
              <span className="text-white/80">{displayText}</span>
              <span className="text-cyber-400 animate-blink">▋</span>
            </div>
          </div>

          {/* Floating agent icons */}
          {AGENT_CONFIGS.slice(0, 4).map((agent, i) => (
            <motion.div
              key={agent.id}
              className="absolute hidden md:flex items-center gap-1.5 glass px-2.5 py-1.5 rounded-lg border border-white/10 text-xs text-white/70"
              style={{
                [i % 2 === 0 ? "left" : "right"]: "-8rem",
                top: `${20 + i * 22}%`,
              }}
              animate={{
                y: [0, -5, 0],
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 3,
                delay: i * 0.5,
                repeat: Infinity,
              }}
            >
              <span className="w-1.5 h-1.5 bg-cyber-400 rounded-full animate-pulse" />
              {agent.name}
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
        >
          <Link href="/builder">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="btn-cyber px-8 py-3.5 rounded-xl font-semibold flex items-center gap-2 text-base"
            >
              <Bot className="w-5 h-5" />
              Build with Cybabot
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </Link>

          <Link href="/marketplace">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="px-8 py-3.5 rounded-xl font-semibold flex items-center gap-2 text-base glass border border-white/15 text-white/80 hover:text-white hover:border-white/30 transition-all"
            >
              <Play className="w-4 h-4" fill="currentColor" />
              Browse Marketplace
            </motion.button>
          </Link>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-8 text-sm text-muted-foreground mb-16"
        >
          {[
            { value: "7", label: "AI Agents" },
            { value: "5yr", label: "Tick Data" },
            { value: "5", label: "LLM Providers" },
            { value: "4", label: "Export Formats" },
            { value: "100%", label: "Open Source" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl font-black gradient-text-cyber">{stat.value}</div>
              <div className="text-xs mt-0.5">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Agent visualization */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ delay: 0.7 }}
        className="relative w-full max-w-4xl mx-auto px-4 pb-16"
      >
        <div className="glass-card p-4 sm:p-6">
          <div className="text-xs text-muted-foreground font-mono mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            CYBABOT ULTRA — LIVE PIPELINE
          </div>

          {/* Agent pipeline visualization */}
          <div className="flex items-center gap-1 sm:gap-2 overflow-x-auto no-scrollbar">
            {AGENT_CONFIGS.map((agent, i) => (
              <React.Fragment key={agent.id}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.8 + i * 0.1 }}
                  className="flex-shrink-0 flex flex-col items-center gap-1 p-2 sm:p-3 rounded-lg glass border border-white/10 min-w-[70px] sm:min-w-[80px]"
                >
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                    style={{
                      background: `radial-gradient(ellipse at center, ${agent.glowColor} 0%, transparent 70%)`,
                    }}
                  >
                    {agent.id}
                  </div>
                  <div className="text-[10px] text-center text-white/60 leading-tight">
                    {agent.name.split(" ")[0]}
                  </div>
                </motion.div>
                {i < AGENT_CONFIGS.length - 1 && (
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ delay: 0.9 + i * 0.1 }}
                    className="flex-shrink-0 h-px w-4 sm:w-6 bg-gradient-to-r from-cyber-500/50 to-cyan-500/50"
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-muted-foreground/50"
      >
        <ChevronDown className="w-5 h-5" />
      </motion.div>
    </section>
  );
}
