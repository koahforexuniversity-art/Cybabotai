"use client";

import React, { useRef } from "react";
import { motion, useInView } from "framer-motion";
import {
  Brain, Shield, BarChart3, Zap, Download, Globe,
  Image, FileText, Link2, Layers, Settings2, Cpu,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "7-Agent AI Crew",
    description: "Sequential + parallel CrewAI pipeline. Each agent is a specialist: hypothesis, data, risk, backtest, performance, optimization, and assembly.",
    color: "from-violet-500 to-purple-500",
    glow: "rgba(139,92,246,0.3)",
  },
  {
    icon: Image,
    title: "Multi-Modal Input",
    description: "Upload chart screenshots, PDFs of strategies, paste URLs. AI vision (Claude/Gemini) analyzes images and extracts rules automatically.",
    color: "from-blue-500 to-cyan-500",
    glow: "rgba(59,130,246,0.3)",
  },
  {
    icon: Cpu,
    title: "5 LLM Providers",
    description: "Choose Grok, Claude, DeepSeek, Gemini, or local Ollama. Assign different models per agent — use GPT-4 class for design, faster models for data.",
    color: "from-amber-500 to-orange-500",
    glow: "rgba(245,158,11,0.3)",
  },
  {
    icon: BarChart3,
    title: "Tick-Level Precision",
    description: "Dukascopy 5-year tick data. Every pip calculated with decimal.Decimal. Real spreads, swaps, margin, slippage — zero float drift.",
    color: "from-cyber-500 to-teal-500",
    glow: "rgba(14,184,166,0.3)",
  },
  {
    icon: Shield,
    title: "Risk Management AI",
    description: "Dedicated risk agent calculates position sizing, max drawdown limits, Kelly criterion, and margin requirements before any backtest runs.",
    color: "from-emerald-500 to-green-500",
    glow: "rgba(16,185,129,0.3)",
  },
  {
    icon: Download,
    title: "4 Export Formats",
    description: "One-click export to MQL5 EA (MT4/MT5), PineScript v6 (TradingView), Python class, and Jupyter notebook. PDF report included.",
    color: "from-pink-500 to-rose-500",
    glow: "rgba(236,72,153,0.3)",
  },
  {
    icon: Layers,
    title: "Monte Carlo Engine",
    description: "10,000 simulation runs to stress-test your strategy. Confidence intervals at 90/95/99%. Walk-forward optimization included in Full mode.",
    color: "from-indigo-500 to-blue-500",
    glow: "rgba(99,102,241,0.3)",
  },
  {
    icon: Globe,
    title: "Marketplace",
    description: "Buy and sell proven bots. Full equity curves, metrics, and backtest reports for every listing. 20% platform commission supports development.",
    color: "from-teal-500 to-cyan-500",
    glow: "rgba(20,184,166,0.3)",
  },
  {
    icon: Settings2,
    title: "Optimization Guardian",
    description: "Genetic algorithm + grid search finds the parameter sweet spot. Penalizes over-fitting using out-of-sample validation automatically.",
    color: "from-orange-500 to-red-500",
    glow: "rgba(249,115,22,0.3)",
  },
];

export function FeaturesSection() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-24 px-4">
      <div className="container mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          className="text-center mb-16"
        >
          <div className="badge-cyber inline-flex px-4 py-1.5 rounded-full mb-4 text-xs">
            CAPABILITIES
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white mb-4">
            Everything You Need to{" "}
            <span className="gradient-text-cyber">Trade Algorithmically</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            ForexPrecision RoboQuant combines institutional-grade backtesting
            with cutting-edge AI to deliver production-ready trading bots.
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.08 }}
              whileHover={{ y: -4 }}
              className="glass-card p-6 group cursor-default"
            >
              {/* Icon */}
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg`}
                style={{ boxShadow: `0 8px 24px ${feature.glow}` }}
              >
                <feature.icon className="w-6 h-6 text-white" />
              </div>

              <h3 className="text-base font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
