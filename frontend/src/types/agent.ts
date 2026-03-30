// ========================================
// Agent & Cybabot Types
// ========================================

export type AgentId = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export type AgentStatus = "idle" | "active" | "success" | "error" | "waiting";

export type LLMProvider =
  | "grok"
  | "claude"
  | "deepseek"
  | "gemini"
  | "ollama";

export interface LLMModel {
  provider: LLMProvider;
  model: string;
  label: string;
  supportsVision: boolean;
  contextWindow: number;
}

export interface AgentConfig {
  id: AgentId;
  name: string;
  role: string;
  description: string;
  icon: string;
  animationType:
    | "brain"
    | "scanner"
    | "shield"
    | "speedometer"
    | "radar"
    | "gear"
    | "notebook";
  color: string;
  glowColor: string;
  llm: LLMModel;
}

export interface AgentStreamMessage {
  type:
    | "agent_start"
    | "agent_progress"
    | "agent_complete"
    | "agent_error"
    | "crew_complete"
    | "crew_start"
    | "heartbeat";
  agent_id?: AgentId;
  message: string;
  timestamp: number;
  data?: AgentStreamData;
}

export interface AgentStreamData {
  // Agent 2 - Data Scout
  symbol?: string;
  period?: string;
  ticks?: number;
  spread_avg?: number;
  swap_long?: number;
  swap_short?: number;

  // Agent 3 - Risk Specialist
  max_drawdown?: number;
  risk_per_trade?: number;
  lot_size?: number;
  margin_required?: number;

  // Agent 4 - Backtesting Agent
  equity_point?: { x: number; y: number; timestamp: number };
  equity_curve?: Array<{ x: number; y: number; timestamp: number }>;

  // Agent 5 - Performance Analyst
  radar_data?: RadarDataPoint;
  metrics?: BacktestMetrics;

  // Agent 6 - Optimization Guardian
  optimization_round?: number;
  optimization_score?: number;
  parameters?: Record<string, number | string>;

  // Agent 7 - Notebook Assembler
  exports?: ExportFiles;
  strategy_id?: string;

  // General
  progress?: number;
  status_text?: string;
  hypothesis?: StrategyHypothesis;
}

export interface StrategyHypothesis {
  name: string;
  description: string;
  type: StrategyType;
  timeframe: string;
  pair: string;
  indicators: string[];
  entry_rules: string[];
  exit_rules: string[];
  risk_reward: number;
}

export type StrategyType =
  | "trend_following"
  | "mean_reversion"
  | "breakout"
  | "scalping"
  | "swing"
  | "grid"
  | "arbitrage"
  | "carry_trade";

export interface RadarDataPoint {
  profitability: number;      // 0-100
  consistency: number;        // 0-100
  risk_management: number;    // 0-100
  drawdown: number;           // 0-100
  win_rate: number;           // 0-100
  recovery: number;           // 0-100
}

export interface BacktestMetrics {
  net_profit: number;
  profit_factor: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  average_win: number;
  average_loss: number;
  expectancy: number;
  recovery_factor: number;
  consecutive_wins: number;
  consecutive_losses: number;
  gross_profit: number;
  gross_loss: number;
  initial_balance: number;
  final_balance: number;
  return_pct: number;
  annual_return_pct: number;
  monte_carlo?: MonteCarloResult;
}

export interface MonteCarloResult {
  confidence_90: number;
  confidence_95: number;
  confidence_99: number;
  worst_case_drawdown: number;
  probability_profit: number;
  simulations: number;
}

export interface ExportFiles {
  mql5_ea?: string;
  pinescript?: string;
  python_class?: string;
  jupyter_notebook?: string;
  pdf_report?: string;
}

export type BuildMode = "quick" | "standard" | "full";

export interface BuildModeConfig {
  mode: BuildMode;
  label: string;
  description: string;
  credits: number;
  agents: AgentId[];
  features: string[];
  recommended?: boolean;
}

export const BUILD_MODES: BuildModeConfig[] = [
  {
    mode: "quick",
    label: "Quick Build",
    description: "Strategy hypothesis + basic backtest",
    credits: 25,
    agents: [1, 2, 4],
    features: ["Strategy rules", "5-year backtest", "Basic metrics"],
  },
  {
    mode: "standard",
    label: "Standard Build",
    description: "Full 7-agent pipeline",
    credits: 75,
    agents: [1, 2, 3, 4, 5, 6, 7],
    features: [
      "Strategy rules",
      "Tick-level data",
      "Risk management",
      "Full backtest",
      "Performance analysis",
      "Optimization",
      "All exports",
    ],
    recommended: true,
  },
  {
    mode: "full",
    label: "Full Build + Monte Carlo",
    description: "Full pipeline + 10,000 Monte Carlo simulations",
    credits: 150,
    agents: [1, 2, 3, 4, 5, 6, 7],
    features: [
      "Everything in Standard",
      "Monte Carlo simulation",
      "Walk-forward optimization",
      "Robustness testing",
      "PDF report",
    ],
  },
];

export const LLM_MODELS: LLMModel[] = [
  { provider: "claude", model: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet", supportsVision: true, contextWindow: 200000 },
  { provider: "claude", model: "claude-3-opus-20240229", label: "Claude 3 Opus", supportsVision: true, contextWindow: 200000 },
  { provider: "grok", model: "grok-2-1212", label: "Grok 2", supportsVision: false, contextWindow: 131072 },
  { provider: "grok", model: "grok-vision-beta", label: "Grok Vision", supportsVision: true, contextWindow: 8192 },
  { provider: "gemini", model: "gemini-1.5-pro", label: "Gemini 1.5 Pro", supportsVision: true, contextWindow: 2000000 },
  { provider: "gemini", model: "gemini-1.5-flash", label: "Gemini 1.5 Flash", supportsVision: true, contextWindow: 1000000 },
  { provider: "deepseek", model: "deepseek-chat", label: "DeepSeek Chat", supportsVision: false, contextWindow: 128000 },
  { provider: "deepseek", model: "deepseek-coder", label: "DeepSeek Coder", supportsVision: false, contextWindow: 128000 },
  { provider: "ollama", model: "llama3.2", label: "Llama 3.2 (Local)", supportsVision: false, contextWindow: 128000 },
  { provider: "ollama", model: "mistral", label: "Mistral (Local)", supportsVision: false, contextWindow: 32000 },
];

export const AGENT_CONFIGS: AgentConfig[] = [
  {
    id: 1,
    name: "Hypothesis Designer",
    role: "Strategy Architect",
    description: "Converting your idea into precise trading rules",
    icon: "Brain",
    animationType: "brain",
    color: "violet",
    glowColor: "rgba(139, 92, 246, 0.6)",
    llm: LLM_MODELS[0],
  },
  {
    id: 2,
    name: "Data Scout",
    role: "Market Intelligence",
    description: "Fetching 5-year tick data + spreads & swaps",
    icon: "Search",
    animationType: "scanner",
    color: "blue",
    glowColor: "rgba(59, 130, 246, 0.6)",
    llm: LLM_MODELS[4],
  },
  {
    id: 3,
    name: "Risk Specialist",
    role: "Capital Protection",
    description: "Calculating safe exposure & drawdown limits",
    icon: "Shield",
    animationType: "shield",
    color: "amber",
    glowColor: "rgba(245, 158, 11, 0.6)",
    llm: LLM_MODELS[0],
  },
  {
    id: 4,
    name: "Backtesting Agent",
    role: "Historical Simulator",
    description: "Running tick-level precision backtest",
    icon: "Gauge",
    animationType: "speedometer",
    color: "cyan",
    glowColor: "rgba(14, 184, 166, 0.6)",
    llm: LLM_MODELS[6],
  },
  {
    id: 5,
    name: "Performance Analyst",
    role: "Metrics Expert",
    description: "Analyzing Sharpe, Sortino, drawdown & edge",
    icon: "BarChart3",
    animationType: "radar",
    color: "emerald",
    glowColor: "rgba(16, 185, 129, 0.6)",
    llm: LLM_MODELS[4],
  },
  {
    id: 6,
    name: "Optimization Guardian",
    role: "Robustness Engineer",
    description: "Refining parameters for live market resilience",
    icon: "Settings2",
    animationType: "gear",
    color: "orange",
    glowColor: "rgba(249, 115, 22, 0.6)",
    llm: LLM_MODELS[6],
  },
  {
    id: 7,
    name: "Notebook Assembler",
    role: "Delivery Expert",
    description: "Packaging MQL5, PineScript, Python & PDF",
    icon: "BookOpen",
    animationType: "notebook",
    color: "teal",
    glowColor: "rgba(20, 184, 166, 0.6)",
    llm: LLM_MODELS[7],
  },
];
