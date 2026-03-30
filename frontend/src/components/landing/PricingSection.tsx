"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Check, Zap, Star, Shield } from "lucide-react";

const CREDIT_PACKS = [
  {
    name: "Starter",
    credits: 500,
    price: 9,
    priceId: "price_starter",
    icon: Zap,
    color: "from-cyber-600 to-cyber-500",
    glow: "rgba(14,184,166,0.3)",
    features: ["500 credits", "Standard builds (75cr each)", "6 quick builds (25cr each)", "All LLM providers", "MQL5 & PineScript export"],
    popular: false,
  },
  {
    name: "Builder",
    credits: 1500,
    price: 24,
    priceId: "price_builder",
    icon: Star,
    color: "from-violet-600 to-cyber-500",
    glow: "rgba(139,92,246,0.4)",
    features: ["1,500 credits", "20 standard builds", "Priority queue", "All LLM providers", "Full backtesting suite", "Marketplace listing"],
    popular: true,
  },
  {
    name: "Pro",
    credits: 4000,
    price: 59,
    priceId: "price_pro",
    icon: Shield,
    color: "from-amber-500 to-orange-500",
    glow: "rgba(245,158,11,0.3)",
    features: ["4,000 credits", "53 standard builds", "Priority queue", "All LLM providers", "Full backtesting suite", "Marketplace listing", "API access"],
    popular: false,
  },
];

export function PricingSection() {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  return (
    <section className="py-24 px-4 relative">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 badge-cyber px-4 py-1.5 rounded-full mb-6">
            <Zap className="w-3.5 h-3.5 text-cyber-400" />
            Credit Packs
          </div>
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
            Simple{" "}
            <span className="gradient-text-cyber">Credit Pricing</span>
          </h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">
            Buy credits once, use them anytime. No subscriptions, no hidden fees.
            New accounts get 500 free credits.
          </p>
        </motion.div>

        {/* Pricing cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {CREDIT_PACKS.map((pack, i) => (
            <motion.div
              key={pack.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              className={`relative glass-card p-6 flex flex-col transition-all duration-300 ${
                pack.popular ? "ring-1 ring-cyber-500/50" : ""
              }`}
              style={{
                boxShadow:
                  hoveredIndex === i
                    ? `0 0 40px ${pack.glow}, 0 8px 32px rgba(0,0,0,0.4)`
                    : undefined,
              }}
            >
              {pack.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="badge-cyber px-3 py-1 rounded-full text-xs font-bold">
                    Most Popular
                  </span>
                </div>
              )}

              {/* Icon & Name */}
              <div className="flex items-center gap-3 mb-6">
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${pack.color} flex items-center justify-center`}
                >
                  <pack.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="font-bold text-white">{pack.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {pack.credits.toLocaleString()} credits
                  </div>
                </div>
              </div>

              {/* Price */}
              <div className="mb-6">
                <div className="flex items-end gap-1">
                  <span className="text-4xl font-black text-white">
                    ${pack.price}
                  </span>
                  <span className="text-muted-foreground text-sm mb-1">
                    one-time
                  </span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  ${((pack.price / pack.credits) * 100).toFixed(1)}¢ per credit
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-2.5 flex-1 mb-6">
                {pack.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2 text-sm text-white/70">
                    <Check className="w-4 h-4 text-cyber-400 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                className={`w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                  pack.popular
                    ? "btn-cyber"
                    : "glass border border-white/15 text-white/80 hover:text-white hover:border-white/30"
                }`}
              >
                Get {pack.name} Pack
              </button>
            </motion.div>
          ))}
        </div>

        {/* Free tier note */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-muted-foreground text-sm mt-8"
        >
          Every new account starts with{" "}
          <span className="text-cyber-400 font-semibold">500 free credits</span>
          {" "}— no credit card required.
        </motion.p>
      </div>
    </section>
  );
}
