"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import { getMetrics, getGraphs } from "@/lib/api";
import { MetricsGrid } from "@/components/metrics/MetricsGrid";
import { DecayCurve } from "@/components/charts/DecayCurve";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatPercent } from "@/lib/utils";

export default function MetricsPage() {
  const { id } = useParams<{ id: string }>();

  const { data: metricsData, error: metricsErr } = useSWR(
    id ? `metrics/${id}` : null,
    () => getMetrics(id!)
  );
  const { data: graphsData } = useSWR(
    id ? `graphs/${id}` : null,
    () => getGraphs(id!)
  );

  if (metricsErr) {
    return (
      <div className="text-sm text-red-400 py-8">
        Failed to load metrics. Make sure the experiment has been run.
      </div>
    );
  }

  if (!metricsData) return <LoadingSpinner label="Loading metrics…" />;

  const { snapshots, summary, strategy_name } = metricsData;

  if (snapshots.length === 0) {
    return (
      <EmptyState
        title="No metrics yet"
        message="Run the experiment first. Metrics are collected at each recall interval."
        action={
          <Link href={`/experiments/${id}`} className="text-sm text-primary hover:underline">
            ← Back to experiment
          </Link>
        }
      />
    );
  }

  const latest = snapshots[snapshots.length - 1];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Metrics</h1>
          <p className="text-muted-foreground text-sm">Strategy: {strategy_name}</p>
        </div>
        <Link href={`/experiments/${id}`} className="text-sm text-muted-foreground hover:text-foreground transition">
          ← Experiment
        </Link>
      </div>

      {/* Summary stats */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Peak Accuracy", value: formatPercent(summary.peak_recall_accuracy ?? 0) },
            { label: "Final Accuracy", value: formatPercent(summary.final_recall_accuracy ?? 0) },
            { label: "Survival Score", value: formatPercent(summary.information_survival_score ?? 0) },
            { label: "Total Forgetting", value: formatPercent(Math.abs(summary.total_forgetting ?? 0)) },
          ].map(({ label, value }) => (
            <div key={label} className="rounded-lg border bg-card p-3">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-xl font-bold mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Latest checkpoint grid */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3">
          Latest checkpoint — Turn {latest.turn_number}
        </h2>
        <MetricsGrid snapshot={latest} />
      </div>

      {/* Memory decay curve */}
      {graphsData?.figures?.decay_curve && (
        <div className="rounded-lg border bg-card p-4">
          <h2 className="text-sm font-medium mb-3">Memory Decay Curve</h2>
          <DecayCurve figure={graphsData.figures.decay_curve} />
        </div>
      )}

      {/* Fact survival timeline */}
      {graphsData?.figures?.fact_survival && (
        <div className="rounded-lg border bg-card p-4">
          <h2 className="text-sm font-medium mb-3">Fact Survival Timeline</h2>
          <DecayCurve figure={graphsData.figures.fact_survival} />
        </div>
      )}

      {/* Checkpoints table */}
      <div>
        <h2 className="text-sm font-medium text-muted-foreground mb-3">
          All Checkpoints ({snapshots.length})
        </h2>
        <div className="rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-secondary/50">
              <tr>
                {["Turn", "Accuracy", "LT Recall", "Survival", "Forgetting Rate", "Tokens", "Cost"].map((h) => (
                  <th key={h} className="px-3 py-2 text-left text-xs text-muted-foreground font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {snapshots.map((s) => (
                <tr key={s.turn_number} className="hover:bg-secondary/20 transition">
                  <td className="px-3 py-2 font-mono text-xs">{s.turn_number}</td>
                  <td className="px-3 py-2">{formatPercent(s.memory_recall_accuracy)}</td>
                  <td className="px-3 py-2">{formatPercent(s.long_term_recall_rate)}</td>
                  <td className="px-3 py-2">{formatPercent(s.information_survival_score)}</td>
                  <td className={`px-3 py-2 ${s.forgetting_rate < 0 ? "text-red-400" : "text-green-400"}`}>
                    {s.forgetting_rate.toFixed(4)}
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">{s.total_tokens.toLocaleString()}</td>
                  <td className="px-3 py-2 text-muted-foreground">${s.total_cost_usd.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
