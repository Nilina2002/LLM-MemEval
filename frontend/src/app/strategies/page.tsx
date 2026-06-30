"use client";
import useSWR from "swr";
import Link from "next/link";
import { listStrategies } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";

export default function StrategiesPage() {
  const { data: strategies, error } = useSWR("strategies-list", listStrategies);

  if (error) return <div className="text-sm text-red-400 py-8">Failed to load strategies.</div>;
  if (!strategies) return <LoadingSpinner label="Loading strategies…" />;

  if (strategies.length === 0) {
    return (
      <EmptyState
        title="No strategies registered"
        message="Implement a class extending MemoryStrategy and register it in the StrategyRegistry."
      />
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold">Memory Strategies</h1>
        <p className="text-muted-foreground text-sm mt-1">
          All registered strategies available for benchmarking. Adding a new one requires only a
          single class implementing <code className="text-xs bg-secondary px-1 py-0.5 rounded">MemoryStrategy</code>.
        </p>
      </div>

      <div className="grid gap-3">
        {strategies.map((s) => (
          <div key={s.name} className="rounded-lg border bg-card p-4 space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold font-mono text-sm">{s.name}</p>
              <Link
                href={`/experiments/new?strategy=${s.name}`}
                className="text-xs text-primary hover:underline flex-shrink-0"
              >
                Run benchmark →
              </Link>
            </div>
            <p className="text-sm text-muted-foreground">{s.description}</p>
            <p className="text-xs text-muted-foreground/60 font-mono">{s.class_name}</p>
          </div>
        ))}
      </div>

      <div className="rounded-md bg-secondary/30 border border-border px-4 py-3 text-xs text-muted-foreground space-y-1">
        <p className="font-medium text-foreground">Adding a new strategy</p>
        <ol className="list-decimal list-inside space-y-0.5">
          <li>Create a class extending <code>MemoryStrategy</code> in <code>backend/app/strategies/</code></li>
          <li>Implement <code>build_context()</code>, <code>update_memory()</code>, <code>retrieve()</code>, <code>clear()</code></li>
          <li>Register it: <code>registry.register("my_strategy", MyStrategy, "Description")</code></li>
          <li>Restart the backend — it appears here automatically</li>
        </ol>
      </div>
    </div>
  );
}
