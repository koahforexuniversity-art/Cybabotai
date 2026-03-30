"use client";

import { useState } from "react";
import { Download, FileCode, TrendingUp, FileText, Loader2 } from "lucide-react";
import { exportApi } from "@/lib/api";

interface ExportPanelProps {
  strategyId: string;
  strategyName: string;
  hasBacktestResults: boolean;
}

export default function ExportPanel({
  strategyId,
  strategyName,
  hasBacktestResults,
}: ExportPanelProps) {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (type: string, url: string, filename: string) => {
    setDownloading(type);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("Download failed:", error);
      alert("Download failed. Please try again.");
    } finally {
      setDownloading(null);
    }
  };

  const exports = [
    {
      id: "mql5",
      name: "MQL5 Expert Advisor",
      description: "MT5 trading bot (.mq5 file)",
      icon: FileCode,
      url: exportApi.downloadMQL5(strategyId),
      filename: `${strategyName.replace(/\s+/g, "")}.mq5`,
      color: "from-blue-500 to-blue-600",
      requiresBacktest: false,
    },
    {
      id: "pinescript",
      name: "PineScript Strategy",
      description: "TradingView indicator (.pine file)",
      icon: TrendingUp,
      url: exportApi.downloadPineScript(strategyId),
      filename: `${strategyName.replace(/\s+/g, "")}.pine`,
      color: "from-green-500 to-green-600",
      requiresBacktest: false,
    },
    {
      id: "python",
      name: "Python Class",
      description: "Standalone Python trading class",
      icon: FileCode,
      url: exportApi.downloadPython(strategyId),
      filename: `${strategyName.toLowerCase().replace(/\s+/g, "_")}.py`,
      color: "from-yellow-500 to-yellow-600",
      requiresBacktest: false,
    },
    {
      id: "backtest",
      name: "Backtest Report (CSV)",
      description: "Trade-by-trade backtest results",
      icon: FileText,
      url: exportApi.downloadBacktestCSV(strategyId),
      filename: `${strategyName.replace(/\s+/g, "_")}_backtest.csv`,
      color: "from-purple-500 to-purple-600",
      requiresBacktest: true,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Export Strategy</h3>
        <span className="text-sm text-gray-400">
          {strategyName}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {exports.map((exp) => {
          const Icon = exp.icon;
          const isDisabled = exp.requiresBacktest && !hasBacktestResults;
          const isLoading = downloading === exp.id;

          return (
            <button
              key={exp.id}
              onClick={() => handleDownload(exp.id, exp.url, exp.filename)}
              disabled={isDisabled || isLoading}
              className={`
                relative group flex items-center gap-4 p-4 rounded-lg border
                transition-all duration-200 text-left
                ${
                  isDisabled
                    ? "bg-gray-800 border-gray-700 cursor-not-allowed opacity-50"
                    : "bg-gray-800 border-gray-700 hover:border-gray-500 hover:bg-gray-750 cursor-pointer"
                }
              `}
            >
              {/* Gradient background */}
              <div
                className={`
                  absolute inset-0 rounded-lg opacity-0 group-hover:opacity-10
                  bg-gradient-to-br ${exp.color}
                  transition-opacity duration-200
                `}
              />

              {/* Icon */}
              <div
                className={`
                  relative w-10 h-10 rounded-lg flex items-center justify-center
                  bg-gradient-to-br ${exp.color}
                `}
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                ) : (
                  <Icon className="w-5 h-5 text-white" />
                )}
              </div>

              {/* Content */}
              <div className="relative flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{exp.name}</span>
                  {exp.requiresBacktest && !hasBacktestResults && (
                    <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded">
                      Needs backtest
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400 mt-0.5">
                  {isDisabled
                    ? "Run a backtest first to enable this export"
                    : exp.description}
                </p>
              </div>

              {/* Download icon */}
              {!isDisabled && !isLoading && (
                <Download className="relative w-5 h-5 text-gray-500 group-hover:text-gray-300 transition-colors" />
              )}
            </button>
          );
        })}
      </div>

      {/* Additional info */}
      <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
        <p className="text-xs text-blue-300">
          <strong>Tip:</strong> After downloading, compile the MQL5 file in MetaEditor (MT5) 
          or paste the PineScript into TradingView's Pine Editor. 
          Always backtest on a demo account before live trading.
        </p>
      </div>
    </div>
  );
}
