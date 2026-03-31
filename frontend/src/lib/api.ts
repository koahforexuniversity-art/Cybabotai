/**
 * Axios API client for Cybabot backend.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "/api/backend/api/v1";

export interface ApiError {
  detail: string;
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach JWT token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 and errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    full_name: string | null;
    credits_balance: number;
    is_admin: boolean;
    created_at: string;
  };
}

export const authApi = {
  register: (data: RegisterRequest) =>
    api.post<AuthResponse>("/auth/register", data),

  login: (data: LoginRequest) =>
    api.post<AuthResponse>("/auth/login", data),

  getMe: () =>
    api.get<AuthResponse["user"]>("/auth/me"),
};

// ─── Credits ─────────────────────────────────────────────────────────────────

export interface CreditPack {
  id: string;
  name: string;
  credits: number;
  price_usd: number;
  price_id: string;
}

export interface CreditBalance {
  balance: number;
  total_purchased: number;
  total_used: number;
  total_earned: number;
}

export interface CreditTransaction {
  id: string;
  amount: number;
  type: "purchase" | "build" | "refund" | "earning" | "marketplace_sale" | "marketplace_purchase";
  description: string;
  created_at: string;
}

export const creditsApi = {
  getBalance: () =>
    api.get<CreditBalance>("/credits/balance"),

  getPacks: () =>
    api.get<CreditPack[]>("/credits/packs"),

  createCheckout: (pack_id: string, success_url: string, cancel_url: string) =>
    api.post<{ checkout_url: string }>("/credits/checkout", {
      pack_id,
      success_url,
      cancel_url,
    }),

  getTransactions: (limit = 20, offset = 0) =>
    api.get<CreditTransaction[]>("/credits/transactions", {
      params: { limit, offset },
    }),
};

// ─── Cybabot Builder ──────────────────────────────────────────────────────────

export type BuildType = "quick" | "standard" | "full";
export type BuildStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface BuildRequest {
  name: string;
  description: string;
  symbols: string[];
  timeframes: string[];
  build_type: BuildType;
  llm_provider?: string;
  llm_model?: string;
  custom_params?: Record<string, string>;
}

export interface AgentResult {
  agent: string;
  status: "pending" | "active" | "completed" | "error";
  progress: number;
  message?: string;
  started_at?: string;
  completed_at?: string;
  output?: string;
  error?: string;
}

export interface Strategy {
  id: string;
  user_id: string;
  name: string;
  description: string;
  symbols: string[];
  timeframes: string[];
  build_type: BuildType;
  status: BuildStatus;
  agent_results: AgentResult[];
  config?: Record<string, unknown>;
  backtest_results?: Record<string, unknown>;
  exports?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface BacktestParams {
  symbol: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  initial_balance?: number;
  risk_percent?: number;
  stop_loss_pips?: number;
  take_profit_pips?: number;
  spread_multiplier?: number;
}

export const cybabotApi = {
  createBuild: (data: BuildRequest) =>
    api.post<Strategy>("/cybabot/build", data),

  getStrategies: (limit = 20, offset = 0) =>
    api.get<Strategy[]>("/cybabot/strategies", {
      params: { limit, offset },
    }),

  getStrategy: (id: string) =>
    api.get<Strategy>(`/cybabot/strategies/${id}`),

  cancelBuild: (id: string) =>
    api.post<void>(`/cybabot/strategies/${id}/cancel`),

  deleteStrategy: (id: string) =>
    api.delete<void>(`/cybabot/strategies/${id}`),

  runBacktest: (strategy_id: string, params: BacktestParams) =>
    api.post<Record<string, unknown>>(
      `/cybabot/strategies/${strategy_id}/backtest`,
      params
    ),

  optimizeParams: (strategy_id: string) =>
    api.post<Record<string, unknown>>(
      `/cybabot/strategies/${strategy_id}/optimize`
    ),
};

// ─── Marketplace ─────────────────────────────────────────────────────────────

export type ListingCategory =
  | "scalping"
  | "day_trading"
  | "swing_trading"
  | "trend_following"
  | "mean_reversion"
  | "breakout"
  | "arbitrage";

export type ListingStatus = "draft" | "active" | "suspended" | "archived";

export interface BotListing {
  id: string;
  strategy_id: string;
  seller_id: string;
  seller_name?: string;
  name: string;
  description: string;
  category: ListingCategory;
  tags: string[];
  price_credits: number;
  price_usd?: number;
  preview_images?: string[];
  status: ListingStatus;
  is_featured: boolean;
  total_purchases: number;
  avg_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

export interface CreateListingRequest {
  strategy_id: string;
  name: string;
  description: string;
  category: ListingCategory;
  tags: string[];
  price_credits: number;
  preview_images?: string[];
}

export interface BotReview {
  id: string;
  listing_id: string;
  buyer_id: string;
  buyer_name?: string;
  rating: number;
  comment: string;
  performance_match?: number;
  created_at: string;
}

export interface PurchaseResult {
  purchase_id: string;
  strategy_id: string;
  strategy: Strategy;
  remaining_balance: number;
}

export interface MarketplaceFilters {
  category?: ListingCategory;
  min_rating?: number;
  max_price?: number;
  search?: string;
  sort_by?: "popular" | "newest" | "rating" | "price_low" | "price_high";
}

export const marketplaceApi = {
  getListings: (filters?: MarketplaceFilters) =>
    api.get<BotListing[]>("/marketplace/listings", { params: filters }),

  getListing: (id: string) =>
    api.get<BotListing>(`/marketplace/listings/${id}`),

  getFeatured: () =>
    api.get<BotListing[]>("/marketplace/featured"),

  createListing: (data: CreateListingRequest) =>
    api.post<BotListing>("/marketplace/listings", data),

  updateListing: (id: string, data: Partial<CreateListingRequest>) =>
    api.patch<BotListing>(`/marketplace/listings/${id}`, data),

  deleteListing: (id: string) =>
    api.delete<void>(`/marketplace/listings/${id}`),

  purchaseListing: (id: string) =>
    api.post<PurchaseResult>(`/marketplace/listings/${id}/purchase`),

  getReviews: (listing_id: string) =>
    api.get<BotReview[]>(`/marketplace/listings/${listing_id}/reviews`),

  createReview: (listing_id: string, data: { rating: number; comment: string }) =>
    api.post<BotReview>(`/marketplace/listings/${listing_id}/reviews`, data),

  getMyListings: () =>
    api.get<BotListing[]>("/marketplace/my-listings"),

  getMyPurchases: () =>
    api.get<{ listing: BotListing; purchase_date: string }[]>(
      "/marketplace/my-purchases"
    ),
};

// ─── Admin ────────────────────────────────────────────────────────────────────

export interface PlatformStats {
  total_users: number;
  total_strategies: number;
  total_builds_completed: number;
  total_credits_purchased: number;
  total_marketplace_sales: number;
  revenue_30d: number;
  active_users_24h: number;
  top_strategies: Array<{
    name: string;
    completions: number;
    avg_performance: number;
  }>;
}

export interface UserSummary {
  id: string;
  email: string;
  full_name: string | null;
  credits_balance: number;
  is_admin: boolean;
  total_builds: number;
  total_spent_credits: number;
  created_at: string;
}

export interface AdminPatchUser {
  is_admin?: boolean;
  credits_balance?: number;
}

export const adminApi = {
  getStats: () =>
    api.get<PlatformStats>("/admin/stats"),

  getUsers: (limit = 50, offset = 0) =>
    api.get<UserSummary[]>("/admin/users", {
      params: { limit, offset },
    }),

  getUser: (user_id: string) =>
    api.get<UserSummary>(`/admin/users/${user_id}`),

  patchUser: (user_id: string, data: AdminPatchUser) =>
    api.patch<UserSummary>(`/admin/users/${user_id}`, data),

  deactivateUser: (user_id: string) =>
    api.post<void>(`/admin/users/${user_id}/deactivate`),

  featureListing: (listing_id: string) =>
    api.post<void>(`/admin/listings/${listing_id}/feature`),

  suspendListing: (listing_id: string) =>
    api.post<void>(`/admin/listings/${listing_id}/suspend`),
};

// ─── Export helpers ───────────────────────────────────────────────────────────

export const exportApi = {
  downloadMQL5: (strategy_id: string) =>
    `${API_BASE_URL}/strategies/${strategy_id}/export/mql5`,

  downloadPineScript: (strategy_id: string) =>
    `${API_BASE_URL}/strategies/${strategy_id}/export/pinescript`,

  downloadPython: (strategy_id: string) =>
    `${API_BASE_URL}/strategies/${strategy_id}/export/python`,

  downloadBacktestCSV: (strategy_id: string) =>
    `${API_BASE_URL}/strategies/${strategy_id}/export/backtest`,
};
