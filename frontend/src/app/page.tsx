import React from "react";
import { HeroSection } from "@/components/landing/HeroSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { AgentsPreviewSection } from "@/components/landing/AgentsPreviewSection";
import { PricingSection } from "@/components/landing/PricingSection";
import { StatsSection } from "@/components/landing/StatsSection";
import { CTASection } from "@/components/landing/CTASection";

export default function LandingPage() {
  return (
    <div className="relative">
      <HeroSection />
      <StatsSection />
      <FeaturesSection />
      <AgentsPreviewSection />
      <PricingSection />
      <CTASection />
    </div>
  );
}
