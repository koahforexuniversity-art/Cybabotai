import type { BacktestMetrics, ExportFiles, StrategyHypothesis, BuildMode } from "./agent";

// ========================================
// Strategy & Backtest Types
// ========================================

export interface Strategy {
  id: string;
  userId: string;
  name: string;
  description?: string;
  hypothesis: StrategyHypothesis;
  config: StrategyConfig;
  status: StrategyStatus;
  backtestResults?: BacktestMetrics;
  exports?: ExportFiles;
  buildMode: BuildMode;
  creditsUsed: number;
  createdAt: string;
  updatedAt: string;
}

export type StrategyStatus =
  | "pending"
  | "building"
  | "backtesting"
  | "completed"
  | "failed";

export interface StrategyConfig {
  pair: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  leverage: number;
  commission_per_lot: number;
  use_variable_spread: boolean;
  include_swaps: boolean;
  slippage_model: "fixed" | "random" | "volume";
  slippage_pips?: number;
  agents?: Record<string, string>;  // agentId -> modelId
}

export const FOREX_PAIRS = [
  "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
  "NZDUSD", "USDCAD", "EURGBP", "EURJPY", "GBPJPY",
  "AUDJPY", "CHFJPY", "EURCHF", "EURAUD", "GBPAUD",
] as const;

export type ForexPair = typeof FOREX_PAIRS[number];

export const TIMEFRAMES = [
  { value: "M1", label: "1 Minute" },
  { value: "M5", label: "5 Minutes" },
  { value: "M15", label: "15 Minutes" },
  { value: "M30", label: "30 Minutes" },
  { value: "H1", label: "1 Hour" },
  { value: "H4", label: "4 Hours" },
  { value: "D1", label: "Daily" },
  { value: "W1", label: "Weekly" },
] as const;

export type Timeframe = typeof TIMEFRAMES[number]["value"];

export interface BacktestRequest {
  strategy_idea: string;
  pair: ForexPair;
  timeframe: Timeframe;
  build_mode: BuildMode;
  initial_balance: number;
  leverage: number;
  uploads?: UploadedFile[];
  agent_models?: Record<string, string>;
  session_id: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  type: "image" | "pdf" | "url";
  content?: string;       // base64 for images
  url?: string;           // for URLs
  summary?: string;       // AI-generated summary
}
