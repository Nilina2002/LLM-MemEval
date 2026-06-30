import type { MetricsSnapshot } from "@/lib/types";
import { formatPercent, formatTokens, formatCost } from "@/lib/utils";

interface MetricsGridProps {
  snapshot: MetricsSnapshot;
}

export function MetricsGrid({ snapshot }: MetricsGridProps) {
  const metrics = [
    { label: "Recall Accuracy", value: formatPercent(snapshot.memory_recall_accuracy) },
    { label: "Long-Term Recall", value: formatPercent(snapshot.long_term_recall_rate) },
    { label: "Survival Score", value: formatPercent(snapshot.information_survival_score) },
    { label: "Forgetting Rate", value: snapshot.forgetting_rate.toFixed(4) },
    { label: "Tokens Used", value: formatTokens(snapshot.total_tokens) },
    { label: "API Cost", value: formatCost(snapshot.total_cost_usd) },
    { label: "Avg Latency", value: `${snapshot.avg_latency_ms.toFixed(0)} ms` },
    { label: "Token Efficiency", value: snapshot.token_efficiency.toFixed(3) },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {metrics.map(({ label, value }) => (
        <div key={label} className="rounded-lg border bg-card p-3">
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-lg font-bold mt-0.5">{value}</p>
        </div>
      ))}
    </div>
  );
}
