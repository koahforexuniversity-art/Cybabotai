"use client";

/**
 * AgentCard - Individual animated agent card for the builder UI.
 * Shows agent status with unique animations per agent.
 */

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, XCircle, Loader2, Brain, Search, Shield, Zap, BarChart3, Settings, BookOpen } from "lucide-react";

export type AgentStatus = "idle" | "active" | "success" | "error";

export interface AgentInfo {
  id: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  name: string;
  role: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  glowColor: string;
}

export const AGENTS: AgentInfo[] = [
  {
    id: 1,
    name: "Hypothesis Designer",
    role: "Strategy Architect",
    description: "Designs complete strategy rules from your idea",
    icon: <Brain className="w-6 h-6" />,
    color: "from-violet-500 to-purple-600",
    glowColor: "shadow-violet-500/50",
  },
  {
    id: 2,
    name: "Data Scout",
    role: "Market Data Engineer",
    description: "Fetches & validates Dukascopy tick data",
    icon: <Search className="w-6 h-6" />,
    color: "from-blue-500 to-cyan-600",
    glowColor: "shadow-blue-500/50",
  },
  {
    id: 3,
    name: "Risk Specialist",
    role: "Risk Manager",
    description: "Calculates optimal risk parameters",
    icon: <Shield className="w-6 h-6" />,
    color: "from-emerald-500 to-green-600",
    glowColor: "shadow-emerald-500/50",
  },
  {
    id: 4,
    name: "Backtesting Agent",
    role: "Quant Engineer",
    description: "Runs precision tick-level backtest",
    icon: <Zap className="w-6 h-6" />,
    color: "from-yellow-500 to-orange-600",
    glowColor: "shadow-yellow-500/50",
  },
  {
    id: 5,
    name: "Performance Analyst",
    role: "Performance Analyst",
    description: "Analyzes results & generates insights",
    icon: <BarChart3 className="w-6 h-6" />,
    color: "from-pink-500 to-rose-600",
    glowColor: "shadow-pink-500/50",
  },
  {
    id: 6,
    name: "Optimization Guardian",
    role: "Robustness Expert",
    description: "Optimizes & validates robustness",
    icon: <Settings className="w-6 h-6" />,
    color: "from-orange-500 to-red-600",
    glowColor: "shadow-orange-500/50",
  },
  {
    id: 7,
    name: "Notebook Assembler",
    role: "Export Engineer",
    description: "Assembles MQL5, PineScript & reports",
    icon: <BookOpen className="w-6 h-6" />,
    color: "from-teal-500 to-cyan-600",
    glowColor: "shadow-teal-500/50",
  },
];

interface AgentCardProps {
  agent: AgentInfo;
  status: AgentStatus;
  message?: string;
  progress?: number;
}

export function AgentCard({ agent, status, message, progress }: AgentCardProps) {
  const isActive = status === "active";
  const isSuccess = status === "success";
  const isError = status === "error";
  const isIdle = status === "idle";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: (agent.id - 1) * 0.1 }}
      className={`
        relative rounded-xl border p-4 transition-all duration-500
        ${isIdle ? "border-white/10 bg-white/5 opacity-50" : ""}
        ${isActive ? `border-white/20 bg-white/10 shadow-lg ${agent.glowColor}` : ""}
        ${isSuccess ? "border-emerald-500/30 bg-emerald-500/10" : ""}
        ${isError ? "border-red-500/30 bg-red-500/10" : ""}
      `}
    >
      {/* Active pulse ring */}
      {isActive && (
        <motion.div
          className={`absolute inset-0 rounded-xl bg-gradient-to-r ${agent.color} opacity-10`}
          animate={{ opacity: [0.05, 0.15, 0.05] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <div className="relative flex items-start gap-3">
        {/* Agent Icon */}
        <div
          className={`
            flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center
            bg-gradient-to-br ${agent.color}
            ${isIdle ? "opacity-40" : "opacity-100"}
            ${isActive ? `shadow-lg ${agent.glowColor}` : ""}
          `}
        >
          {isActive ? (
            <motion.div
              animate={{ rotate: agent.id === 6 ? 360 : 0, scale: [1, 1.1, 1] }}
              transition={{
                rotate: { duration: 3, repeat: Infinity, ease: "linear" },
                scale: { duration: 1.5, repeat: Infinity },
              }}
            >
              {agent.icon}
            </motion.div>
          ) : (
            agent.icon
          )}
        </div>

        {/* Agent Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h3 className={`text-sm font-semibold ${isIdle ? "text-white/40" : "text-white"}`}>
                {agent.name}
              </h3>
              <p className={`text-xs ${isIdle ? "text-white/20" : "text-white/50"}`}>
                {agent.role}
              </p>
            </div>

            {/* Status Icon */}
            <div className="flex-shrink-0">
              {isActive && (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Loader2 className="w-4 h-4 text-white/70" />
                </motion.div>
              )}
              {isSuccess && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 500 }}
                >
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                </motion.div>
              )}
              {isError && (
                <motion.div
                  animate={{ x: [-2, 2, -2, 2, 0] }}
                  transition={{ duration: 0.4 }}
                >
                  <XCircle className="w-4 h-4 text-red-400" />
                </motion.div>
              )}
            </div>
          </div>

          {/* Status Message */}
          <AnimatePresence mode="wait">
            {message && !isIdle && (
              <motion.p
                key={message}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                className={`mt-1 text-xs truncate ${
                  isError ? "text-red-400" : isSuccess ? "text-emerald-400" : "text-white/60"
                }`}
              >
                {message}
              </motion.p>
            )}
          </AnimatePresence>

          {/* Progress Bar */}
          {isActive && progress !== undefined && (
            <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className={`h-full bg-gradient-to-r ${agent.color} rounded-full`}
                initial={{ width: "0%" }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
