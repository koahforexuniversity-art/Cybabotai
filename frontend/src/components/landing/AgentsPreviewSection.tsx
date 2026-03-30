"use client";

import React, { useRef, useState } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import {
  Brain, Search, Shield, Gauge, BarChart3, Settings2, BookOpen,
  CheckCircle, Clock,
} from "lucide-react";
import { AGENT_CONFIGS } from "@/types/agent";

const AGENT_ICONS = [Brain, Search, Shield, Gauge, BarChart3, Settings2, BookOpen];

export function AgentsPreviewSection() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  const [activeAgent, setActiveAgent] = useState<number>(1);

  const agent = AGENT_CONFIGS[activeAgent - 1];

  return (
    <section ref={ref} className="py-24 px-4 overflow-hidden">
      <div className="container mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          className="text-center mb-16"
        >
          <div className="badge-cyber inline-flex px-4 py-1.5 rounded-full mb-4 text-xs">
            THE CREW
          </div>
          <h2 className="text-3xl sm:text-4xl font-black text-white mb-4">
            Meet Your{" "}
            <span className="gradient-text-cyber">7 AI Specialists</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Each agent is a domain expert. They run sequentially, passing context
            between them to build the perfect strategy.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8 items-center">
          {/* Agent list */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.2 }}
            className="space-y-2"
          >
            {AGENT_CONFIGS.map((ag, i) => {
              const Icon = AGENT_ICONS[i];
              const isActive = ag.id === activeAgent;
              return (
                <motion.button
                  key={ag.id}
                  onClick={() => setActiveAgent(ag.id)}
                  whileHover={{ x: 4 }}
                  className={`
                    w-full flex items-center gap-4 p-4 rounded-xl border text-left transition-all
                    ${isActive
                      ? "glass border-cyber-500/40 shadow-neon-cyan"
                      : "glass border-white/5 hover:border-white/15"
                    }
                  `}
                >
                  <div
                    className={`
                      w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
                      ${isActive ? "bg-cyber-500/20" : "bg-white/5"}
                    `}
                    style={isActive ? { boxShadow: `0 0 20px ${ag.glowColor}` } : {}}
                  >
                    <Icon className={`w-5 h-5 ${isActive ? "text-cyber-400" : "text-muted-foreground"}`} />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-mono font-bold ${isActive ? "text-cyber-400" : "text-muted-foreground"}`}>
                        AGENT {ag.id}
                      </span>
                      {isActive && (
                        <motion.span
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="w-1.5 h-1.5 bg-emerald-400 rounded-full"
                        />
                      )}
                    </div>
                    <div className={`text-sm font-semibold ${isActive ? "text-white" : "text-white/70"}`}>
                      {ag.name}
                    </div>
                    <div className="text-xs text-muted-foreground truncate">
                      {ag.description}
                    </div>
                  </div>

                  <div className="flex-shrink-0">
                    {isActive ? (
                      <CheckCircle className="w-4 h-4 text-cyber-400" />
                    ) : (
                      <Clock className="w-4 h-4 text-muted-foreground/40" />
                    )}
                  </div>
                </motion.button>
              );
            })}
          </motion.div>

          {/* Agent detail panel */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.3 }}
            className="relative"
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeAgent}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="glass-card p-6"
              >
                {/* Agent header */}
                <div className="flex items-center gap-4 mb-6">
                  <motion.div
                    animate={{
                      boxShadow: [
                        `0 0 10px ${agent.glowColor}`,
                        `0 0 30px ${agent.glowColor}`,
                        `0 0 10px ${agent.glowColor}`,
                      ],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center"
                  >
                    {React.createElement(AGENT_ICONS[activeAgent - 1], {
                      className: "w-7 h-7",
                      style: { color: agent.glowColor },
                    })}
                  </motion.div>
                  <div>
                    <div className="text-xs text-muted-foreground font-mono">
                      AGENT {agent.id} / {AGENT_CONFIGS.length}
                    </div>
                    <div className="text-xl font-bold text-white">{agent.name}</div>
                    <div className="text-sm text-muted-foreground">{agent.role}</div>
                  </div>
                </div>

                {/* Status simulation */}
                <div className="space-y-3 mb-6">
                  <div className="text-xs text-muted-foreground font-mono uppercase tracking-wide">
                    Status
                  </div>
                  <div className="glass rounded-lg p-3 border border-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <motion.div
                        animate={{ opacity: [1, 0.3, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-2 h-2 rounded-full bg-cyber-400"
                      />
                      <span className="text-xs font-mono text-cyber-400">PROCESSING</span>
                    </div>
                    <div className="text-sm text-white/80 font-mono">{agent.description}</div>
                  </div>
                </div>

                {/* LLM info */}
                <div className="glass rounded-lg p-3 border border-white/5">
                  <div className="text-xs text-muted-foreground mb-1.5">Default LLM</div>
                  <div className="flex items-center gap-2">
                    <div className="text-sm font-medium text-white">{agent.llm.label}</div>
                    {agent.llm.supportsVision && (
                      <span className="badge-cyber px-2 py-0.5 rounded text-[10px]">
                        VISION
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {(agent.llm.contextWindow / 1000).toFixed(0)}K context window
                  </div>
                </div>

                {/* Progress indicator */}
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Pipeline position</span>
                    <span>{agent.id} / 7</span>
                  </div>
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(agent.id / 7) * 100}%` }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className="h-full rounded-full progress-cyber"
                    />
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
