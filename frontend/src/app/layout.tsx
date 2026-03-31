import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Toaster } from "sonner";
import { Navbar } from "@/components/layout/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Cybabot — AI Forex Bot Builder",
    template: "%s | Cybabot",
  },
  description:
    "Build production-ready forex trading bots in minutes with Cybabot Ultra — a 7-agent AI crew powered by CrewAI. Backtest with tick-level precision, export to MQL5 & PineScript.",
  keywords: [
    "forex bot builder",
    "algorithmic trading",
    "backtesting",
    "CrewAI",
    "MQL5",
    "PineScript",
    "trading AI",
    "cybabot",
  ],
  authors: [{ name: "Cybabot Team" }],
  creator: "Cybabot",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://cybabotai.com",
    title: "Cybabot — AI Forex Bot Builder",
    description: "AI-powered forex bot builder with 7-agent CrewAI pipeline",
    siteName: "Cybabot",
  },
  twitter: {
    card: "summary_large_image",
    title: "Cybabot Ultra",
    description: "Build production-ready forex bots with AI in minutes",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0f" },
    { media: "(prefers-color-scheme: light)", color: "#0a0a0f" },
  ],
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable} dark`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans antialiased" suppressHydrationWarning>
        {/* Cyber background effects */}
        <div className="fixed inset-0 cyber-grid opacity-30 pointer-events-none -z-10" />
        <div className="fixed inset-0 bg-glow-gradient pointer-events-none -z-10" />

        {/* Animated scan line */}
        <div className="fixed top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyber-500 to-transparent animate-scan opacity-30 pointer-events-none z-50" />

        {/* Main layout */}
        <div className="relative flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1">{children}</main>
        </div>

        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "rgba(10, 10, 15, 0.95)",
              border: "1px solid rgba(14, 184, 166, 0.3)",
              color: "#f0fdf9",
              backdropFilter: "blur(20px)",
            },
          }}
        />
      </body>
    </html>
  );
}
