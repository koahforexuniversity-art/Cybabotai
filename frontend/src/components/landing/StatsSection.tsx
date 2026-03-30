"use client";

import React, { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { TrendingUp, Users, Bot, Zap } from "lucide-react";

const STATS = [
  { icon: Bot, value: "12,847", label: "Bots Built", color: "text-cyber-400", glow: "rgba(14,184,166,0.3)" },
  { icon: Users, value: "3,291", label: "Active Traders", color: "text-violet-400", glow: "rgba(139,92,246,0.3)" },
  { icon: TrendingUp, value: "$2.4M", label: "Backtested Volume", color: "text-emerald-400", glow: "rgba(16,185,129,0.3)" },
  { icon: Zap, value: "98.7%", label: "Uptime", color: "text-amber-400", glow: "rgba(245,158,11,0.3)" },
];

export function StatsSection() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="py-12 border-y border-white/5">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-xl mb-3 ${stat.color}`}
                style={{
                  background: `radial-gradient(ellipse at center, ${stat.glow} 0%, transparent 70%)`,
                  boxShadow: `0 0 20px ${stat.glow}`,
                }}
              >
                <stat.icon className="w-6 h-6" />
              </div>
              <div className={`text-3xl font-black ${stat.color} font-mono`}>
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
