"use client";

/**
 * Strategy Library Page - View and manage user's created strategies.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Plus, Search, Clock, CheckCircle, XCircle, Loader2, Download, Eye } from "lucide-react";

interface Strategy {
  id: string;
  name: string;
  status: "pending" | "processing" | "completed" | "failed";
  build_type: string;
  credits_cost: number;
  progress: number;
  created_at: string;
}

// Demo strategies
const DEMO_STRATEGIES: Strategy[] = [
  {
    id: "1",
    name: "EMA Crossover Scalper",
    status: "completed",
    build_type: "standard",
    credits_cost: 75,
    progress: 100,
    created_at: "2024-12-15T10:30:00Z",
  },
  {
    id: "2",
    name: "London Breakout v2",
    status: "processing",
    build_type: "full",
    credits_cost: 150,
    progress: 65,
    created_at: "2024-12-16T14:20:00Z",
  },
  {
    id: "3",
    name: "RSI Mean Reversion",
    status: "failed",
    build_type: "quick",
    credits_cost: 25,
    progress: 30,
    created_at: "2024-12-14T08:15:00Z",
  },
];

const statusConfig = {
  pending: { icon: Clock, color: "text-white/40", bg: "bg-white/5", label: "Pending" },
  processing: { icon: Loader2, color: "text-blue-400", bg: "bg-blue-500/10", label: "Processing" },
  completed: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-500/10", label: "Complete" },
  failed: { icon: XCircle, color: "text-red-400", bg: "bg-red-500/10", label: "Failed" },
};

export default function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredStrategies = DEMO_STRATEGIES.filter((s) => {
    if (statusFilter !== "all" && s.status !== statusFilter) return false;
    if (searchQuery && !s.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Strategy Library</h1>
            </div>
            <p className="text-white/50 text-sm">
              Manage your created strategies and export files
            </p>
          </div>
          <a
            href="/builder"
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-lg text-sm font-medium text-white hover:from-violet-500 hover:to-purple-500 transition-all"
          >
            <Plus className="w-4 h-4" />
            New Strategy
          </a>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search strategies..."
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-blue-500/50 text-sm"
            />
          </div>
          <div className="flex gap-2">
            {["all", "completed", "processing", "failed"].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  statusFilter === status
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : "bg-white/5 text-white/40 border border-transparent hover:text-white/70"
                }`}
              >
                {status === "all" ? "All" : status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Strategy List */}
        <div className="space-y-3">
          {filteredStrategies.map((strategy, idx) => {
            const statusInfo = statusConfig[strategy.status];
            const StatusIcon = statusInfo.icon;

            return (
              <motion.div
                key={strategy.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex items-center justify-between p-4 rounded-xl border border-white/10 bg-white/5 hover:border-white/20 transition-all"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className={`w-10 h-10 rounded-lg ${statusInfo.bg} flex items-center justify-center`}>
                    <StatusIcon
                      className={`w-4 h-4 ${statusInfo.color} ${strategy.status === "processing" ? "animate-spin" : ""}`}
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-white truncate">{strategy.name}</h3>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className={`text-xs ${statusInfo.color}`}>{statusInfo.label}</span>
                      <span className="text-xs text-white/30">
                        {strategy.build_type} • {strategy.credits_cost} credits
                      </span>
                      <span className="text-xs text-white/20">
                        {new Date(strategy.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    {/* Progress bar for processing */}
                    {strategy.status === "processing" && (
                      <div className="mt-2 h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
                          initial={{ width: "0%" }}
                          animate={{ width: `${strategy.progress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  {strategy.status === "completed" && (
                    <>
                      <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/50 hover:text-white">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-white/50 hover:text-white">
                        <Download className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {filteredStrategies.length === 0 && (
          <div className="text-center py-20">
            <BookOpen className="w-12 h-12 text-white/10 mx-auto mb-3" />
            <p className="text-white/30 text-sm">No strategies found</p>
            <a
              href="/builder"
              className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-violet-500/20 text-violet-400 rounded-lg text-sm hover:bg-violet-500/30 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create your first strategy
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
