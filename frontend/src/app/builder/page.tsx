"use client";

/**
 * Builder Page - Main strategy building interface.
 * Connects to WebSocket for real-time agent streaming.
 */

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Upload, Link, FileText, Image, ChevronDown, Play, Loader2 } from "lucide-react";
import { AgentCrewPanel } from "@/components/builder/AgentCrewPanel";
import type { AgentStatus } from "@/components/builder/AgentCard";
import type { AgentStreamMessage } from "@/hooks/useWebSocket";
import { useWebSocket } from "@/hooks/useWebSocket";

const LLM_PROVIDERS = [
  { id: "claude", name: "Claude (Anthropic)", models: ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"], badge: "Best" },
  { id: "grok", name: "Grok (xAI)", models: ["grok-2-1212", "grok-beta"], badge: "Fast" },
  { id: "gemini", name: "Gemini (Google)", models: ["gemini-1.5-pro", "gemini-1.5-flash"], badge: "Large Context" },
  { id: "deepseek", name: "DeepSeek", models: ["deepseek-chat", "deepseek-coder"], badge: "Code" },
  { id: "ollama", name: "Ollama (Local)", models: ["llama3.2", "mistral", "codellama"], badge: "Free" },
];

const BUILD_TYPES = [
  { id: "quick", name: "Quick Build", credits: 25, description: "Strategy design + risk analysis (Agents 1-3)", time: "~2 min" },
  { id: "standard", name: "Standard Build", credits: 75, description: "Full 7-agent pipeline with backtest", time: "~8 min" },
  { id: "full", name: "Full Build + Monte Carlo", credits: 150, description: "Complete analysis with Monte Carlo simulation", time: "~15 min" },
];

type InputType = "text" | "url" | "image" | "pdf";

export default function BuilderPage() {
  // Form state
  const [inputType, setInputType] = useState<InputType>("text");
  const [inputText, setInputText] = useState("");
  const [inputUrl, setInputUrl] = useState("");
  const [selectedProvider, setSelectedProvider] = useState("claude");
  const [selectedModel, setSelectedModel] = useState("claude-3-5-sonnet-20241022");
  const [buildType, setBuildType] = useState("standard");
  const [strategyName, setStrategyName] = useState("");

  // Build state
  const [isBuilding, setIsBuilding] = useState(false);
  const [strategyId, setStrategyId] = useState<string | null>(null);
  const [buildComplete, setBuildComplete] = useState(false);

  // Agent states
  const [agentStatuses, setAgentStatuses] = useState<Record<number, AgentStatus>>({
    1: "idle", 2: "idle", 3: "idle", 4: "idle", 5: "idle", 6: "idle", 7: "idle",
  });
  const [agentMessages, setAgentMessages] = useState<Record<number, string>>({});
  const [agentProgress, setAgentProgress] = useState<Record<number, number>>({});

  // Results state
  const [equityCurve, setEquityCurve] = useState<Array<{ x: number; y: number }>>([]);
  const [radarData, setRadarData] = useState<Record<string, number> | null>(null);
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [exports, setExports] = useState<Record<string, string> | null>(null);

  // WebSocket message handler
  const handleMessage = useCallback((message: AgentStreamMessage) => {
    const { type, agent_id, msg, data } = message as AgentStreamMessage & { msg?: string };
    const messageText = message.message || msg || "";

    setAgentStatuses((prev) => ({
      ...prev,
      [agent_id]: type === "agent_start" || type === "agent_progress"
        ? "active"
        : type === "agent_complete"
        ? "success"
        : type === "agent_error"
        ? "error"
        : prev[agent_id],
    }));

    if (messageText) {
      setAgentMessages((prev) => ({ ...prev, [agent_id]: messageText }));
    }

    if (data?.progress !== undefined) {
      setAgentProgress((prev) => ({ ...prev, [agent_id]: data.progress! }));
    }

    if (data?.equity_point) {
      setEquityCurve((prev) => [...prev, data.equity_point!]);
    }

    if (data?.radar_data) {
      setRadarData(data.radar_data);
    }

    if (data?.metrics) {
      setMetrics(data.metrics);
    }

    if (type === "crew_complete") {
      setBuildComplete(true);
      setIsBuilding(false);
      if (data?.exports) {
        setExports(data.exports as Record<string, string>);
      }
    }
  }, []);

  // Get auth token from localStorage
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;

  // WebSocket connection
  useWebSocket({
    strategyId,
    token,
    onMessage: handleMessage,
    onConnect: () => console.log("WebSocket connected"),
    onDisconnect: () => console.log("WebSocket disconnected"),
  });

  const handleStartBuild = async () => {
    if (!inputText && !inputUrl) return;
    if (!strategyName) return;

    setIsBuilding(true);
    setBuildComplete(false);
    setEquityCurve([]);
    setRadarData(null);
    setMetrics(null);
    setExports(null);

    // Reset agent statuses
    setAgentStatuses({ 1: "idle", 2: "idle", 3: "idle", 4: "idle", 5: "idle", 6: "idle", 7: "idle" });
    setAgentMessages({});
    setAgentProgress({});

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/cybabot/build`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: strategyName,
          input_text: inputType === "text" ? inputText : inputUrl,
          input_type: inputType,
          llm_provider: selectedProvider,
          llm_model: selectedModel,
          build_type: buildType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start build");
      }

      const data = await response.json();
      setStrategyId(data.id);
    } catch (error) {
      console.error("Build failed:", error);
      setIsBuilding(false);
    }
  };

  const selectedBuildType = BUILD_TYPES.find((b) => b.id === buildType);
  const selectedProviderInfo = LLM_PROVIDERS.find((p) => p.id === selectedProvider);

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Strategy Builder</h1>
          </div>
          <p className="text-white/50 text-sm">
            Describe your trading idea and let 7 AI agents build a complete, backtested strategy
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Input */}
          <div className="lg:col-span-2 space-y-6">
            {/* Strategy Name */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5">
              <label className="block text-sm font-medium text-white/70 mb-2">
                Strategy Name
              </label>
              <input
                type="text"
                value={strategyName}
                onChange={(e) => setStrategyName(e.target.value)}
                placeholder="e.g., EMA Crossover Scalper"
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50 transition-colors"
              />
            </div>

            {/* Input Type Selector */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5">
              <label className="block text-sm font-medium text-white/70 mb-3">
                Strategy Input
              </label>

              {/* Input Type Tabs */}
              <div className="flex gap-2 mb-4">
                {[
                  { id: "text", label: "Text", icon: <FileText className="w-3.5 h-3.5" /> },
                  { id: "url", label: "URL", icon: <Link className="w-3.5 h-3.5" /> },
                  { id: "image", label: "Image", icon: <Image className="w-3.5 h-3.5" /> },
                  { id: "pdf", label: "PDF", icon: <Upload className="w-3.5 h-3.5" /> },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setInputType(tab.id as InputType)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      inputType === tab.id
                        ? "bg-violet-500/20 text-violet-400 border border-violet-500/30"
                        : "text-white/40 hover:text-white/70 border border-transparent"
                    }`}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Text Input */}
              {inputType === "text" && (
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Describe your trading strategy idea in detail...

Example: 'I want a strategy that trades EURUSD on the 1-hour chart using EMA crossovers. Enter long when the 20 EMA crosses above the 50 EMA, and short when it crosses below. Use ATR-based stop loss and 2:1 risk-reward ratio. Only trade during London and New York sessions.'"
                  rows={8}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-violet-500/50 transition-colors resize-none text-sm"
                />
              )}

              {/* URL Input */}
              {inputType === "url" && (
                <input
                  type="url"
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  placeholder="https://example.com/trading-strategy-article"
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/30 focus:outline-none focus:border-violet-500/50 transition-colors"
                />
              )}

              {/* File Upload */}
              {(inputType === "image" || inputType === "pdf") && (
                <div className="border-2 border-dashed border-white/10 rounded-lg p-8 text-center hover:border-violet-500/30 transition-colors cursor-pointer">
                  <Upload className="w-8 h-8 text-white/30 mx-auto mb-2" />
                  <p className="text-white/40 text-sm">
                    Drop your {inputType === "image" ? "chart screenshot" : "PDF document"} here
                  </p>
                  <p className="text-white/20 text-xs mt-1">
                    {inputType === "image" ? "PNG, JPG up to 10MB" : "PDF up to 20MB"}
                  </p>
                </div>
              )}
            </div>

            {/* LLM Provider Selection */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5">
              <label className="block text-sm font-medium text-white/70 mb-3">
                AI Model
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
                {LLM_PROVIDERS.map((provider) => (
                  <button
                    key={provider.id}
                    onClick={() => {
                      setSelectedProvider(provider.id);
                      setSelectedModel(provider.models[0]);
                    }}
                    className={`relative p-3 rounded-lg border text-left transition-all ${
                      selectedProvider === provider.id
                        ? "border-violet-500/50 bg-violet-500/10"
                        : "border-white/10 bg-white/5 hover:border-white/20"
                    }`}
                  >
                    {provider.badge && (
                      <span className="absolute top-1.5 right-1.5 text-[10px] px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-400">
                        {provider.badge}
                      </span>
                    )}
                    <p className="text-xs font-medium text-white pr-8">{provider.name}</p>
                  </button>
                ))}
              </div>

              {/* Model selector */}
              {selectedProviderInfo && (
                <div className="relative">
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-violet-500/50 appearance-none cursor-pointer"
                  >
                    {selectedProviderInfo.models.map((model) => (
                      <option key={model} value={model} className="bg-[#1a1a2e]">
                        {model}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40 pointer-events-none" />
                </div>
              )}
            </div>

            {/* Build Type Selection */}
            <div className="rounded-xl border border-white/10 bg-white/5 p-5">
              <label className="block text-sm font-medium text-white/70 mb-3">
                Build Type
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {BUILD_TYPES.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setBuildType(type.id)}
                    className={`p-4 rounded-lg border text-left transition-all ${
                      buildType === type.id
                        ? "border-violet-500/50 bg-violet-500/10"
                        : "border-white/10 bg-white/5 hover:border-white/20"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-white">{type.name}</span>
                      <span className="text-xs text-violet-400 font-mono">{type.credits}cr</span>
                    </div>
                    <p className="text-xs text-white/40">{type.description}</p>
                    <p className="text-xs text-white/30 mt-1">{type.time}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Start Build Button */}
            <button
              onClick={handleStartBuild}
              disabled={isBuilding || (!inputText && !inputUrl) || !strategyName}
              className={`w-full py-4 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
                isBuilding || (!inputText && !inputUrl) || !strategyName
                  ? "bg-white/5 text-white/30 cursor-not-allowed"
                  : "bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-500 hover:to-purple-500 shadow-lg shadow-violet-500/25"
              }`}
            >
              {isBuilding ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Building Strategy...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Start Build ({selectedBuildType?.credits} credits)
                </>
              )}
            </button>
          </div>

          {/* Right Panel - Agent Crew */}
          <div className="space-y-6">
            <AgentCrewPanel
              agentStatuses={agentStatuses}
              agentMessages={agentMessages}
              agentProgress={agentProgress}
            />

            {/* Results Panel */}
            <AnimatePresence>
              {buildComplete && metrics && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-5"
                >
                  <h3 className="text-sm font-semibold text-emerald-400 mb-3">
                    ✅ Strategy Complete
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { label: "Return", value: `${metrics.total_return_pct?.toFixed(1)}%` },
                      { label: "Sharpe", value: metrics.sharpe_ratio?.toFixed(2) },
                      { label: "Win Rate", value: `${metrics.win_rate?.toFixed(1)}%` },
                      { label: "Max DD", value: `${metrics.max_drawdown_pct?.toFixed(1)}%` },
                    ].map((stat) => (
                      <div key={stat.label} className="bg-white/5 rounded-lg p-2">
                        <p className="text-xs text-white/40">{stat.label}</p>
                        <p className="text-sm font-semibold text-white">{stat.value}</p>
                      </div>
                    ))}
                  </div>

                  {exports && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs text-white/50">Downloads:</p>
                      {Object.keys(exports).map((key) => (
                        <button
                          key={key}
                          className="w-full text-left text-xs px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-colors"
                        >
                          📄 {key}
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
