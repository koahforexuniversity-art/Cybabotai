"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot, Zap, Store, LayoutDashboard, BookOpen, Menu, X,
  ChevronDown, LogIn, LogOut, User, Settings, Shield,
} from "lucide-react";
import { CreditBadge } from "@/components/credits/CreditBadge";
import { BuyCreditsModal } from "@/components/credits/BuyCreditsModal";
import { cn } from "@/lib/utils";
import { getUser, clearAuth, refreshUser, type AuthUser } from "@/lib/auth";

const NAV_ITEMS = [
  { href: "/builder", label: "Builder", icon: Bot, description: "Build forex bots with Cybabot" },
  { href: "/library", label: "Library", icon: BookOpen, description: "Your strategy collection" },
  { href: "/marketplace", label: "Marketplace", icon: Store, description: "Buy & sell trading bots" },
];

export function Navbar() {
  const pathname = usePathname();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCreditsOpen, setIsCreditsOpen] = useState(false);
  const [isUserOpen, setIsUserOpen] = useState(false);
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    setAuthUser(getUser());
    // Refresh live balance from server on each navigation
    refreshUser().then((u) => { if (u) setAuthUser(u); });
  }, [pathname]);

  // Poll credit balance every 30s while logged in
  useEffect(() => {
    if (!authUser) return;
    const interval = setInterval(() => {
      refreshUser().then((u) => { if (u) setAuthUser(u); });
    }, 30000);
    return () => clearInterval(interval);
  }, [!!authUser]);

  const user = authUser
    ? { name: authUser.name || authUser.email, email: authUser.email, credits: authUser.credits_balance, role: authUser.role }
    : null;

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setIsMobileOpen(false);
  }, [pathname]);

  return (
    <>
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={cn(
          "sticky top-0 z-50 w-full transition-all duration-300",
          isScrolled
            ? "frosted border-b border-white/5 shadow-glass"
            : "bg-transparent"
        )}
      >
        <nav className="container mx-auto flex h-16 items-center justify-between px-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="relative"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyber-500 to-cyan-400 flex items-center justify-center shadow-neon-cyan">
                <Bot className="w-5 h-5 text-black" />
              </div>
              <div className="absolute -inset-1 rounded-xl bg-cyber-500/20 blur-sm -z-10 group-hover:bg-cyber-500/40 transition-all" />
            </motion.div>
            <div className="hidden sm:block">
              <div className="text-sm font-bold text-white leading-none">
                Cyba<span className="gradient-text-cyber">bot</span>
              </div>
              <div className="text-xs text-muted-foreground leading-none mt-0.5">
                Ultra
              </div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Link key={item.href} href={item.href}>
                  <motion.div
                    whileHover={{ y: -1 }}
                    className={cn(
                      "flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                      isActive
                        ? "text-cyber-400 bg-cyber-500/10 border border-cyber-500/20"
                        : "text-muted-foreground hover:text-white hover:bg-white/5"
                    )}
                  >
                    <item.icon className="w-4 h-4" />
                    {item.label}
                    {isActive && (
                      <motion.div
                        layoutId="navIndicator"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyber-500"
                      />
                    )}
                  </motion.div>
                </Link>
              );
            })}
          </div>

          {/* Right side: Credits + User */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                {/* Credit Badge */}
                <CreditBadge
                  credits={user.credits}
                  onBuyClick={() => setIsCreditsOpen(true)}
                />

                {/* User Menu */}
                <div className="relative">
                  <button
                    onClick={() => setIsUserOpen(!isUserOpen)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass border border-white/10 hover:border-cyber-500/30 transition-all"
                  >
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyber-500 to-violet-500 flex items-center justify-center text-xs font-bold text-white">
                      {user.name[0].toUpperCase()}
                    </div>
                    <span className="hidden sm:block text-sm text-white/80">
                      {user.name.split(" ")[0]}
                    </span>
                    <ChevronDown className={cn("w-3.5 h-3.5 text-muted-foreground transition-transform", isUserOpen && "rotate-180")} />
                  </button>

                  <AnimatePresence>
                    {isUserOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 8, scale: 0.96 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 8, scale: 0.96 }}
                        transition={{ duration: 0.15 }}
                        className="absolute right-0 mt-2 w-56 glass-card p-1 shadow-glass-lg"
                        onMouseLeave={() => setIsUserOpen(false)}
                      >
                        <div className="px-3 py-2 border-b border-white/10 mb-1">
                          <div className="text-sm font-medium text-white">{user.name}</div>
                          <div className="text-xs text-muted-foreground">{user.email}</div>
                        </div>
                        <MenuItem icon={User} label="Profile" href="/profile" />
                        <MenuItem icon={Settings} label="Settings" href="/settings" />
                        {user.role === "admin" && (
                          <MenuItem icon={LayoutDashboard} label="Admin" href="/admin" />
                        )}
                        <div className="border-t border-white/10 mt-1 pt-1">
                          <button
                            onClick={() => { clearAuth(); setAuthUser(null); }}
                            className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                          >
                            <LogOut className="w-4 h-4" />
                            Sign Out
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </>
            ) : (
              <Link href="/auth">
                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  className="flex items-center gap-2 px-4 py-1.5 rounded-lg btn-cyber text-sm font-semibold"
                >
                  <LogIn className="w-4 h-4" />
                  Sign In
                </motion.button>
              </Link>
            )}

            {/* Mobile menu button */}
            <button
              className="md:hidden p-2 rounded-lg glass border border-white/10"
              onClick={() => setIsMobileOpen(!isMobileOpen)}
            >
              {isMobileOpen ? (
                <X className="w-5 h-5 text-white" />
              ) : (
                <Menu className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </nav>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {isMobileOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden frosted border-t border-white/5"
            >
              <div className="container mx-auto px-4 py-4 flex flex-col gap-1">
                {NAV_ITEMS.map((item, i) => (
                  <motion.div
                    key={item.href}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-3 rounded-xl transition-all",
                        pathname.startsWith(item.href)
                          ? "bg-cyber-500/10 text-cyber-400 border border-cyber-500/20"
                          : "text-muted-foreground hover:text-white hover:bg-white/5"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <div>
                        <div className="text-sm font-medium">{item.label}</div>
                        <div className="text-xs opacity-60">{item.description}</div>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>

      {/* Buy Credits Modal */}
      <BuyCreditsModal
        isOpen={isCreditsOpen}
        onClose={() => setIsCreditsOpen(false)}
        currentCredits={user?.credits ?? 0}
      />
    </>
  );
}

function MenuItem({
  icon: Icon,
  label,
  href,
}: {
  icon: React.ElementType;
  label: string;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
    >
      <Icon className="w-4 h-4" />
      {label}
    </Link>
  );
}
