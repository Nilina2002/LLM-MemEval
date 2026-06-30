"use client";
import { useState } from "react";
import useSWR from "swr";
import { listExperiments, compareExperiments } from "@/lib/api";
import { StrategyComparison } from "@/components/charts/StrategyComparison";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { formatPercent, formatCost } from "@/lib/utils";
import type { Experiment, PlotlyFigure } from "@/lib/types";

export default function ComparePage() {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    experiments: Experiment[];
    comparison_chart: PlotlyFigure;
  } | null>(null);

  const { data: expData } = useSWR("experiments-compare-list", () => listExperiments(200, 0));
  const completed = expData?.experiments.filter((e) => e.status === "completed") ?? [];

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
    setResult(null);
  }

  async function handleCompare() {
    if (selected.size < 2) { setError("Select at least 2 experiments to compare."); return; }
    setComparing(true);
    setError(null);
    try {
      const data = await compareExperiments(Array.from(selected));
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Comparison failed.");
    } finally {
      setComparing(false);
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Strategy Comparison</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Select completed experiments to overlay their memory decay curves.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/15 border border-destructive/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Experiment selector */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-muted-foreground">
            Completed Experiments ({completed.length})
          </h2>
          {selected.size > 0 && (
            <span className="text-xs text-primary">{selected.size} selected</span>
          )}
        </div>

        {!expData ? (
          <LoadingSpinner />
        ) : completed.length === 0 ? (
          <p className="text-sm text-muted-foreground py-4">
            No completed experiments yet. Run at least 2 experiments to compare.
          </p>
        ) : (
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {completed.map((exp) => (
              <button
                key={exp.id}
                onClick={() => toggle(exp.id)}
                className={`w-full text-left rounded-lg border p-3 transition ${
                  selected.has(exp.id)
                    ? "border-primary bg-primary/10"
                    : "border-border bg-card hover:border-primary/40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{exp.name}</p>
                    <p className="text-xs text-muted-foreground">{exp.strategy_name}</p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                    <StatusBadge status={exp.status} />
                    {selected.has(exp.id) && (
                      <span className="text-primary text-sm">✓</span>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={handleCompare}
        disabled={comparing || selected.size < 2}
        className="bg-primary text-primary-foreground px-5 py-2.5 rounded-md text-sm font-medium disabled:opacity-50 hover:opacity-90 transition"
      >
        {comparing ? "Comparing…" : `Compare ${selected.size} Experiment${selected.size !== 1 ? "s" : ""}`}
      </button>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Overlay chart */}
          <div className="rounded-lg border bg-card p-4">
            <h2 className="text-sm font-medium mb-3">Memory Decay Comparison</h2>
            <StrategyComparison figure={result.comparison_chart} />
          </div>

          {/* Side-by-side stats */}
          <div>
            <h2 className="text-sm font-medium text-muted-foreground mb-3">
              Summary ({result.experiments.length} experiments)
            </h2>
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-secondary/50">
                  <tr>
                    {["Experiment", "Strategy", "Turns", "Cost"].map((h) => (
                      <th key={h} className="px-3 py-2 text-left text-xs text-muted-foreground font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {result.experiments.map((exp) => (
                    <tr key={exp.id} className="hover:bg-secondary/20 transition">
                      <td className="px-3 py-2 font-medium">{exp.name}</td>
                      <td className="px-3 py-2 text-muted-foreground">{exp.strategy_name}</td>
                      <td className="px-3 py-2">{exp.total_turns}</td>
                      <td className="px-3 py-2">{formatCost(exp.total_cost_usd)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
