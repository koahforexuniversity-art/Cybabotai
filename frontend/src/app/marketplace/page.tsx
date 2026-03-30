"use client";

/**
 * Marketplace Page - Browse and purchase bot strategies.
 */

import { useState } from "react";
import { motion } from "framer-motion";
import { Store, Search, Filter, Star, TrendingUp, Shield, Zap } from "lucide-react";

const CATEGORIES = [
  { id: "all", name: "All Bots", count: 0 },
  { id: "scalping", name: "Scalping", count: 0 },
  { id: "swing", name: "Swing Trading", count: 0 },
  { id: "trend_following", name: "Trend Following", count: 0 },
  { id: "mean_reversion", name: "Mean Reversion", count: 0 },
  { id: "grid", name: "Grid", count: 0 },
  { id: "arbitrage", name: "Arbitrage", count: 0 },
];

interface BotListing {
  id: string;
  title: string;
  description: string;
  category: string;
  price_credits: number;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  win_rate: number | null;
  total_return: number | null;
  sales_count: number;
  rating: number;
  review_count: number;
  featured: boolean;
}

// Demo listings for preview
const DEMO_LISTINGS: BotListing[] = [
  {
    id: "1",
    title: "EMA Crossover Pro",
    description: "Trend-following strategy using 20/50 EMA crossovers with ATR-based risk management",
    category: "trend_following",
    price_credits: 500,
    sharpe_ratio: 1.85,
    max_drawdown: -12.3,
    win_rate: 58.2,
    total_return: 45.6,
    sales_count: 142,
    rating: 4.5,
    review_count: 38,
    featured: true,
  },
  {
    id: "2",
    title: "London Breakout Scalper",
    description: "High-frequency scalper targeting London session breakouts with tight risk control",
    category: "scalping",
    price_credits: 750,
    sharpe_ratio: 2.12,
    max_drawdown: -8.5,
    win_rate: 65.1,
    total_return: 32.4,
    sales_count: 89,
    rating: 4.8,
    review_count: 25,
    featured: true,
  },
  {
    id: "3",
    title: "Bollinger Bounce",
    description: "Mean reversion strategy using Bollinger Bands with RSI confirmation",
    category: "mean_reversion",
    price_credits: 350,
    sharpe_ratio: 1.42,
    max_drawdown: -15.7,
    win_rate: 52.8,
    total_return: 28.9,
    sales_count: 67,
    rating: 4.2,
    review_count: 18,
    featured: false,
  },
];

export default function MarketplacePage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("created_at");

  const filteredListings = DEMO_LISTINGS.filter((l) => {
    if (selectedCategory !== "all" && l.category !== selectedCategory) return false;
    if (searchQuery && !l.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <Store className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Bot Marketplace</h1>
          </div>
          <p className="text-white/50 text-sm">
            Browse community-built bots with verified backtest results
          </p>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search bots..."
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 focus:outline-none focus:border-emerald-500/50 text-sm"
            />
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-emerald-500/50 appearance-none cursor-pointer"
          >
            <option value="created_at" className="bg-[#1a1a2e]">Newest</option>
            <option value="rating" className="bg-[#1a1a2e]">Top Rated</option>
            <option value="sales" className="bg-[#1a1a2e]">Best Selling</option>
            <option value="price_asc" className="bg-[#1a1a2e]">Price: Low to High</option>
            <option value="price_desc" className="bg-[#1a1a2e]">Price: High to Low</option>
          </select>
        </div>

        {/* Category Filters */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex-shrink-0 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
                selectedCategory === cat.id
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-white/5 text-white/40 border border-transparent hover:text-white/70"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Bot Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredListings.map((listing, idx) => (
            <motion.div
              key={listing.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="relative rounded-xl border border-white/10 bg-white/5 p-5 hover:border-white/20 transition-all group cursor-pointer"
            >
              {listing.featured && (
                <div className="absolute top-3 right-3 px-2 py-0.5 bg-gradient-to-r from-amber-500 to-orange-500 rounded text-[10px] font-semibold text-white">
                  FEATURED
                </div>
              )}

              <h3 className="text-sm font-semibold text-white mb-1 pr-20">{listing.title}</h3>
              <p className="text-xs text-white/40 mb-4 line-clamp-2">{listing.description}</p>

              {/* Performance Metrics */}
              <div className="grid grid-cols-2 gap-2 mb-4">
                <div className="flex items-center gap-1.5">
                  <TrendingUp className="w-3 h-3 text-emerald-400" />
                  <span className="text-xs text-white/70">
                    {listing.total_return !== null ? `${listing.total_return}%` : "—"} return
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Shield className="w-3 h-3 text-blue-400" />
                  <span className="text-xs text-white/70">
                    {listing.max_drawdown !== null ? `${listing.max_drawdown}%` : "—"} DD
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Zap className="w-3 h-3 text-yellow-400" />
                  <span className="text-xs text-white/70">
                    {listing.sharpe_ratio !== null ? listing.sharpe_ratio.toFixed(2) : "—"} Sharpe
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Star className="w-3 h-3 text-amber-400" />
                  <span className="text-xs text-white/70">
                    {listing.win_rate !== null ? `${listing.win_rate}%` : "—"} win
                  </span>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-white/5">
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                  <span className="text-xs text-white/60">{listing.rating}</span>
                  <span className="text-xs text-white/30">({listing.review_count})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-white/30">{listing.sales_count} sales</span>
                  <span className="text-sm font-semibold text-emerald-400">
                    {listing.price_credits} cr
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredListings.length === 0 && (
          <div className="text-center py-20">
            <Store className="w-12 h-12 text-white/10 mx-auto mb-3" />
            <p className="text-white/30 text-sm">No bots found matching your criteria</p>
          </div>
        )}
      </div>
    </div>
  );
}
