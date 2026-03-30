import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCredits(credits: number): string {
  if (credits >= 1_000_000) return `${(credits / 1_000_000).toFixed(1)}M`;
  if (credits >= 1_000) return `${(credits / 1_000).toFixed(1)}k`;
  return credits.toLocaleString();
}

export function formatCurrency(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatPercent(value: number, decimals = 2): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number, decimals = 2): string {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return `${str.slice(0, maxLength)}...`;
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function generateId(prefix = ""): string {
  const random = Math.random().toString(36).slice(2, 11);
  const ts = Date.now().toString(36);
  return prefix ? `${prefix}_${ts}${random}` : `${ts}${random}`;
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
  });
}

export function getFileType(file: File): "image" | "pdf" | "unknown" {
  if (file.type.startsWith("image/")) return "image";
  if (file.type === "application/pdf") return "pdf";
  return "unknown";
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function lerp(start: number, end: number, t: number): number {
  return start + (end - start) * t;
}

export function getColorForValue(
  value: number,
  min: number,
  max: number
): string {
  const pct = clamp((value - min) / (max - min), 0, 1);
  if (pct < 0.33) return "text-red-400";
  if (pct < 0.66) return "text-amber-400";
  return "text-emerald-400";
}

export function getMetricColor(value: number, type: "profit" | "drawdown" | "ratio"): string {
  switch (type) {
    case "profit":
      return value >= 0 ? "text-emerald-400" : "text-red-400";
    case "drawdown":
      if (value <= -30) return "text-red-400";
      if (value <= -15) return "text-amber-400";
      return "text-emerald-400";
    case "ratio":
      if (value >= 2) return "text-emerald-400";
      if (value >= 1) return "text-amber-400";
      return "text-red-400";
    default:
      return "text-white";
  }
}

export function isValidUrl(str: string): boolean {
  try {
    new URL(str);
    return true;
  } catch {
    return false;
  }
}

export const PROVIDER_COLORS: Record<string, string> = {
  claude: "from-orange-500 to-amber-500",
  grok: "from-gray-600 to-gray-400",
  gemini: "from-blue-500 to-purple-500",
  deepseek: "from-indigo-500 to-blue-500",
  ollama: "from-green-500 to-emerald-500",
};

export const PROVIDER_LABELS: Record<string, string> = {
  claude: "Claude",
  grok: "Grok",
  gemini: "Gemini",
  deepseek: "DeepSeek",
  ollama: "Ollama",
};
