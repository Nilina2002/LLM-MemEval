import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCost(usd: number): string {
  return usd < 0.01 ? `$${(usd * 100).toFixed(2)}¢` : `$${usd.toFixed(4)}`;
}

export function formatTokens(n: number): string {
  return n >= 1_000_000
    ? `${(n / 1_000_000).toFixed(1)}M`
    : n >= 1_000
    ? `${(n / 1_000).toFixed(1)}K`
    : String(n);
}

export function formatPercent(ratio: number): string {
  return `${(ratio * 100).toFixed(1)}%`;
}

export function statusColor(status: string): string {
  switch (status) {
    case "completed": return "text-green-400";
    case "running":   return "text-blue-400";
    case "failed":    return "text-red-400";
    case "pending":   return "text-yellow-400";
    default:          return "text-gray-400";
  }
}
