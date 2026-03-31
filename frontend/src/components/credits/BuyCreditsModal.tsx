"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X, Zap, CheckCircle, Loader2, CreditCard, Gift, Star, Rocket,
} from "lucide-react";
import { getToken } from "@/lib/auth";

interface CreditPack {
  id: string;
  label: string;
  price: string;
  credits: number;
  bonus?: number;
  popular?: boolean;
  icon: React.ElementType;
  color: string;
}

const CREDIT_PACKS: CreditPack[] = [
  { id: "starter",    label: "Starter",    price: "₦5,000",  credits: 500,   icon: Zap,    color: "from-blue-500 to-cyan-500" },
  { id: "builder",    label: "Builder",    price: "₦10,000", credits: 2000,  bonus: 0,   popular: true, icon: Rocket, color: "from-cyber-500 to-cyan-400" },
  { id: "pro",        label: "Pro",        price: "₦25,000", credits: 6000,  bonus: 1000, icon: Star,   color: "from-violet-500 to-purple-500" },
  { id: "enterprise", label: "Enterprise", price: "₦50,000", credits: 15000, bonus: 3000, icon: Gift,   color: "from-amber-500 to-orange-500" },
];

interface BuyCreditsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentCredits: number;
}

export function BuyCreditsModal({ isOpen, onClose, currentCredits }: BuyCreditsModalProps) {
  const [selectedPack, setSelectedPack] = useState<string>("builder");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePurchase = async () => {
    const pack = CREDIT_PACKS.find((p) => p.id === selectedPack);
    if (!pack) return;
    setIsLoading(true);
    setError(null);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api/backend";
      const callbackUrl = `${window.location.origin}/credits/verify`;

      const response = await fetch(`${backendUrl}/api/v1/credits/checkout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ pack_id: pack.id, callback_url: callbackUrl }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Checkout failed");

      // Redirect to Paystack payment page
      window.location.href = data.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Payment failed");
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", duration: 0.4 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-2xl px-4"
          >
            <div className="glass-card p-6 shadow-glass-lg">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-cyber-400" fill="currentColor" />
                    Buy Credits
                  </h2>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Balance:{" "}
                    <span className="text-cyber-400 font-mono font-bold">
                      {currentCredits.toLocaleString()}
                    </span>{" "}
                    credits
                  </p>
                </div>
                <button
                  onClick={onClose}
                  className="w-8 h-8 rounded-lg glass border border-white/10 flex items-center justify-center text-muted-foreground hover:text-white transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Credit Packs */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                {CREDIT_PACKS.map((pack) => (
                  <motion.button
                    key={pack.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedPack(pack.id)}
                    className={`relative p-4 rounded-xl border text-left transition-all ${
                      selectedPack === pack.id
                        ? "border-cyber-500/50 bg-cyber-500/10 shadow-neon-cyan"
                        : "border-white/10 bg-white/3 hover:border-white/20"
                    }`}
                  >
                    {pack.popular && (
                      <div className="absolute -top-2 left-1/2 -translate-x-1/2">
                        <span className="badge-cyber px-2 py-0.5 rounded-full text-xs">POPULAR</span>
                      </div>
                    )}
                    <div className="flex items-start justify-between mb-3">
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${pack.color} flex items-center justify-center`}>
                        <pack.icon className="w-5 h-5 text-white" />
                      </div>
                      {selectedPack === pack.id && <CheckCircle className="w-4 h-4 text-cyber-400" />}
                    </div>
                    <div className="text-base font-bold text-white">{pack.label}</div>
                    <div className="text-2xl font-black text-white mt-1">{pack.price}</div>
                    <div className="text-sm text-cyber-400 font-mono mt-1">
                      {pack.credits.toLocaleString()} credits
                      {pack.bonus ? (
                        <span className="text-emerald-400 ml-1">+{pack.bonus.toLocaleString()} bonus</span>
                      ) : null}
                    </div>
                    <div className="text-xs text-muted-foreground mt-2">
                      ≈ {Math.floor((pack.credits + (pack.bonus || 0)) / 75)} standard builds
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Credit cost reference */}
              <div className="glass rounded-xl p-3 mb-5 border border-white/5">
                <div className="text-xs text-muted-foreground mb-2 font-medium uppercase tracking-wide">
                  Credit Costs
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-center">
                  {[
                    { label: "Quick Build", cost: 25 },
                    { label: "Standard Build", cost: 75 },
                    { label: "Full + Monte Carlo", cost: 150 },
                  ].map((item) => (
                    <div key={item.label}>
                      <div className="text-cyber-400 font-mono font-bold">{item.cost}</div>
                      <div className="text-muted-foreground">{item.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {error && (
                <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-4">
                  {error}
                </div>
              )}

              {/* Purchase Button */}
              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={handlePurchase}
                disabled={isLoading}
                className="w-full btn-cyber py-3 rounded-xl font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Redirecting to Paystack...
                  </>
                ) : (
                  <>
                    <CreditCard className="w-4 h-4" />
                    Pay {CREDIT_PACKS.find((p) => p.id === selectedPack)?.price} via Paystack
                  </>
                )}
              </motion.button>

              <p className="text-center text-xs text-muted-foreground mt-3">
                Secure payment via Paystack · Credits never expire
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
