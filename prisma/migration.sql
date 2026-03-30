-- ============================================
-- Cybabot Ultra - Supabase PostgreSQL Migration
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Users Table
-- ============================================
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "email" TEXT UNIQUE NOT NULL,
    "name" TEXT,
    "password_hash" TEXT NOT NULL,
    "credits_balance" INTEGER DEFAULT 500,
    "role" TEXT DEFAULT 'user',
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Credit Transactions Table
-- ============================================
CREATE TABLE IF NOT EXISTS "credit_transactions" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "amount" INTEGER NOT NULL,
    "type" TEXT NOT NULL,
    "description" TEXT,
    "stripe_session_id" TEXT,
    "related_strategy_id" UUID,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "credit_transactions_user_id_idx" ON "credit_transactions"("user_id");

-- ============================================
-- Strategies Table
-- ============================================
CREATE TABLE IF NOT EXISTS "strategies" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "user_id" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "config" TEXT DEFAULT '{}',
    "input_type" TEXT DEFAULT 'text',
    "input_data" TEXT,
    "llm_provider" TEXT DEFAULT 'groq',
    "llm_model" TEXT,
    "backtest_results" TEXT,
    "equity_curve" TEXT,
    "status" TEXT DEFAULT 'pending',
    "progress" INTEGER DEFAULT 0,
    "error_message" TEXT,
    "exports" TEXT DEFAULT '{}',
    "build_type" TEXT,
    "credits_cost" INTEGER,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "strategies_user_id_idx" ON "strategies"("user_id");
CREATE INDEX IF NOT EXISTS "strategies_status_idx" ON "strategies"("status");

-- ============================================
-- Bot Listings Table (Marketplace)
-- ============================================
CREATE TABLE IF NOT EXISTS "bot_listings" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "seller_id" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "strategy_id" UUID UNIQUE NOT NULL REFERENCES "strategies"("id") ON DELETE CASCADE,
    "title" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "price_credits" INTEGER NOT NULL,
    "price_usd" DOUBLE PRECISION,
    "sharpe_ratio" DOUBLE PRECISION,
    "max_drawdown" DOUBLE PRECISION,
    "win_rate" DOUBLE PRECISION,
    "total_return" DOUBLE PRECISION,
    "sales_count" INTEGER DEFAULT 0,
    "rating" DOUBLE PRECISION DEFAULT 0,
    "review_count" INTEGER DEFAULT 0,
    "featured" BOOLEAN DEFAULT false,
    "active" BOOLEAN DEFAULT true,
    "thumbnail_url" TEXT,
    "equity_curve_url" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "bot_listings_seller_id_idx" ON "bot_listings"("seller_id");
CREATE INDEX IF NOT EXISTS "bot_listings_category_idx" ON "bot_listings"("category");
CREATE INDEX IF NOT EXISTS "bot_listings_active_idx" ON "bot_listings"("active");
CREATE INDEX IF NOT EXISTS "bot_listings_featured_idx" ON "bot_listings"("featured");

-- ============================================
-- Bot Purchases Table
-- ============================================
CREATE TABLE IF NOT EXISTS "bot_purchases" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "buyer_id" UUID NOT NULL REFERENCES "users"("id") ON DELETE CASCADE,
    "listing_id" UUID NOT NULL REFERENCES "bot_listings"("id") ON DELETE CASCADE,
    "credits_paid" INTEGER NOT NULL,
    "usd_paid" DOUBLE PRECISION,
    "stripe_session_id" TEXT,
    "platform_fee" INTEGER NOT NULL,
    "seller_earnings" INTEGER NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "bot_purchases_buyer_id_idx" ON "bot_purchases"("buyer_id");
CREATE INDEX IF NOT EXISTS "bot_purchases_listing_id_idx" ON "bot_purchases"("listing_id");

-- ============================================
-- Bot Reviews Table
-- ============================================
CREATE TABLE IF NOT EXISTS "bot_reviews" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "listing_id" UUID NOT NULL REFERENCES "bot_listings"("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL,
    "rating" INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    "comment" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE("listing_id", "user_id")
);

CREATE INDEX IF NOT EXISTS "bot_reviews_listing_id_idx" ON "bot_reviews"("listing_id");

-- ============================================
-- Admin Settings Table
-- ============================================
CREATE TABLE IF NOT EXISTS "admin_settings" (
    "id" UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    "key" TEXT UNIQUE NOT NULL,
    "value" TEXT NOT NULL,
    "description" TEXT,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS on all tables
ALTER TABLE "users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "credit_transactions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "strategies" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "bot_listings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "bot_purchases" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "bot_reviews" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "admin_settings" ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view their own profile" ON "users" FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON "users" FOR UPDATE USING (auth.uid() = id);

-- Credit transactions policies
CREATE POLICY "Users can view their own transactions" ON "credit_transactions" FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own transactions" ON "credit_transactions" FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Strategies policies
CREATE POLICY "Users can view their own strategies" ON "strategies" FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create their own strategies" ON "strategies" FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own strategies" ON "strategies" FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own strategies" ON "strategies" FOR DELETE USING (auth.uid() = user_id);

-- Bot listings policies (public read, owner write)
CREATE POLICY "Anyone can view active listings" ON "bot_listings" FOR SELECT USING (active = true);
CREATE POLICY "Sellers can manage their listings" ON "bot_listings" FOR ALL USING (auth.uid() = seller_id);

-- Bot purchases policies
CREATE POLICY "Buyers can view their purchases" ON "bot_purchases" FOR SELECT USING (auth.uid() = buyer_id);

-- Bot reviews policies
CREATE POLICY "Anyone can view reviews" ON "bot_reviews" FOR SELECT USING (true);
CREATE POLICY "Authenticated users can create reviews" ON "bot_reviews" FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Admin settings policies
CREATE POLICY "Admins can manage settings" ON "admin_settings" FOR ALL USING (
    EXISTS (SELECT 1 FROM "users" WHERE "id" = auth.uid() AND "role" = 'admin')
);

-- ============================================
-- Functions and Triggers
-- ============================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON "users" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON "strategies" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bot_listings_updated_at BEFORE UPDATE ON "bot_listings" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bot_reviews_updated_at BEFORE UPDATE ON "bot_reviews" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_admin_settings_updated_at BEFORE UPDATE ON "admin_settings" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Done!
-- ============================================
