"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, ArrowRight, Github } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-24 px-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-cyber-500/10 rounded-full blur-3xl" />
      </div>

      <div className="max-w-3xl mx-auto text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          {/* Icon */}
          <div className="flex justify-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyber-500 to-cyan-400 flex items-center justify-center shadow-neon-cyan">
              <Bot className="w-8 h-8 text-black" />
            </div>
          </div>

          {/* Headline */}
          <h2 className="text-4xl sm:text-5xl font-black text-white mb-6 leading-tight">
            Ready to Build Your{" "}
            <span className="gradient-text-cyber">First Forex Bot?</span>
          </h2>

          <p className="text-muted-foreground text-lg mb-10 max-w-xl mx-auto">
            Join traders using Cybabot Ultra to automate their strategies.
            Start free — 500 credits included, no credit card needed.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/builder">
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="btn-cyber px-8 py-4 rounded-xl font-bold flex items-center gap-2 text-base"
              >
                <Bot className="w-5 h-5" />
                Start Building Free
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            </Link>

            <a
              href="https://github.com/koahforexuniversity-art/Cybabotai"
              target="_blank"
              rel="noopener noreferrer"
            >
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="px-8 py-4 rounded-xl font-bold flex items-center gap-2 text-base glass border border-white/15 text-white/80 hover:text-white hover:border-white/30 transition-all"
              >
                <Github className="w-5 h-5" />
                View on GitHub
              </motion.button>
            </a>
          </div>

          {/* Trust signals */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground"
          >
            {["Open Source", "No subscription", "500 free credits", "5 LLM providers"].map((item) => (
              <div key={item} className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-cyber-400" />
                {item}
              </div>
            ))}
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
