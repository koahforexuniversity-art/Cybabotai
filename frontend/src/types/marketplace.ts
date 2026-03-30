import type { BacktestMetrics, StrategyType } from "./agent";

// ========================================
// Marketplace Types
// ========================================

export interface BotListing {
  id: string;
  sellerId: string;
  sellerName: string;
  sellerAvatar?: string;
  strategyId: string;
  title: string;
  description: string;
  longDescription?: string;
  category: BotCategory;
  tags: string[];
  price: number;           // in credits
  priceUsd?: number;       // optional USD price
  currency: "credits" | "usd";
  metrics: BacktestMetrics;
  screenshotUrl?: string;
  equityCurveData: Array<{ x: number; y: number }>;
  pair: string;
  timeframe: string;
  strategyType: StrategyType;
  reviews: BotReview[];
  averageRating: number;
  totalReviews: number;
  salesCount: number;
  isVerified: boolean;
  isFeatured: boolean;
  createdAt: string;
  updatedAt: string;
  expiresAt?: string;
}

export type BotCategory =
  | "scalping"
  | "swing"
  | "trend_following"
  | "mean_reversion"
  | "grid"
  | "breakout"
  | "arbitrage"
  | "carry_trade"
  | "news_trading"
  | "multi_strategy";

export interface BotReview {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  listingId: string;
  rating: number;        // 1-5
  title: string;
  body: string;
  verified: boolean;     // verified purchase
  helpful: number;       // upvotes
  createdAt: string;
}

export interface MarketplaceFilters {
  category?: BotCategory;
  minPrice?: number;
  maxPrice?: number;
  minWinRate?: number;
  minSharpe?: number;
  maxDrawdown?: number;
  pair?: string;
  timeframe?: string;
  sortBy: MarketplaceSortBy;
  search?: string;
}

export type MarketplaceSortBy =
  | "newest"
  | "popular"
  | "highest_rated"
  | "price_low"
  | "price_high"
  | "best_performance";

export interface BotPurchase {
  id: string;
  buyerId: string;
  listingId: string;
  listing: BotListing;
  creditsPaid: number;
  purchasedAt: string;
  downloadsRemaining: number;
}

export interface SellerStats {
  totalSales: number;
  totalRevenue: number;
  averageRating: number;
  totalListings: number;
  activeListings: number;
}

export interface MarketplacePagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface MarketplaceResponse {
  listings: BotListing[];
  pagination: MarketplacePagination;
}
