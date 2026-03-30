"use client";

import React from "react";
import { motion } from "framer-motion";
import { Zap, Plus } from "lucide-react";
import { formatCredits } from "@/lib/utils";

interface CreditBadgeProps {
  credits: number;
  onBuyClick?: () => void;
  className?: string;
}

export function CreditBadge({ credits, onBuyClick, className }: CreditBadgeProps) {
  const isLow = credits < 100;
  const isCritical = credits < 25;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center gap-1 ${className ?? ""}`}
    >
      <button
        onClick={onBuyClick}
        className={`
          flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
          transition-all duration-200 border
          ${
            isCritical
              ? "bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20"
              : isLow
              ? "bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20"
              : "bg-cyber-500/10 border-cyber-500/20 text-cyber-400 hover:bg-cyber-500/20"
          }
        `}
      >
        <Zap
          className={`w-3.5 h-3.5 ${isCritical ? "animate-pulse" : ""}`}
          fill="currentColor"
        />
        <span className="font-mono font-bold">{formatCredits(credits)}</span>
        <span className="text-xs opacity-60 hidden sm:inline">credits</span>
      </button>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onBuyClick}
        className="w-7 h-7 rounded-lg btn-cyber flex items-center justify-center"
        title="Buy Credits"
      >
        <Plus className="w-3.5 h-3.5" />
      </motion.button>
    </motion.div>
  );
}
