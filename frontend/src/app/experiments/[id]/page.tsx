"use client";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { runExperiment, deleteExperiment } from "@/lib/api";
import { useExperiment } from "@/hooks/useExperiment";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { formatTokens, formatCost } from "@/lib/utils";

export default function ExperimentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { experiment, refresh } = useExperiment(id ?? null);
  const [running, setRunning] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!experiment) return <LoadingSpinner label="Loading experiment…" />;

  async function handleRun() {
    if (!experiment) return;
    setRunning(true);
    setError(null);
    try {
      await runExperiment(experiment.id);
      await refresh();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to start experiment.";
      setError(msg);
    } finally {
      setRunning(false);
    }
  }

  async function handleDelete() {
    if (!experiment) return;
    if (!confirm(`Delete experiment "${experiment.name}"? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteExperiment(experiment.id);
      router.push("/experiments");
    } catch {
      setError("Failed to delete experiment.");
      setDeleting(false);
    }
  }

  const canRun = experiment.status === "pending" || experiment.status === "failed";

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold truncate">{experiment.name}</h1>
            <StatusBadge status={experiment.status} />
          </div>
          {experiment.description && (
            <p className="text-muted-foreground text-sm mt-1">{experiment.description}</p>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/15 border border-destructive/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetaStat label="Strategy" value={experiment.strategy_name} />
        <MetaStat label="Turns" value={String(experiment.total_turns || "—")} />
        <MetaStat label="Tokens" value={formatTokens(experiment.total_tokens)} />
        <MetaStat label="Cost" value={formatCost(experiment.total_cost_usd)} />
        {experiment.duration_seconds != null && (
          <MetaStat label="Duration" value={`${experiment.duration_seconds.toFixed(1)}s`} />
        )}
        {experiment.started_at && (
          <MetaStat
            label="Started"
            value={new Date(experiment.started_at).toLocaleString()}
          />
        )}
        {experiment.completed_at && (
          <MetaStat
            label="Completed"
            value={new Date(experiment.completed_at).toLocaleString()}
          />
        )}
      </div>

      {/* Error message */}
      {experiment.error_message && (
        <div className="rounded-md bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm">
          <p className="font-medium text-red-400 mb-1">Experiment failed</p>
          <pre className="text-muted-foreground text-xs whitespace-pre-wrap">
            {experiment.error_message}
          </pre>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 flex-wrap">
        {canRun && (
          <button
            onClick={handleRun}
            disabled={running}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium disabled:opacity-60 hover:opacity-90 transition"
          >
            {running ? "Starting…" : "▶ Run Experiment"}
          </button>
        )}
        {experiment.status === "completed" && (
          <>
            <Link
              href={`/experiments/${id}/metrics`}
              className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:opacity-90 transition"
            >
              Metrics & Charts
            </Link>
            <Link
              href={`/experiments/${id}/facts`}
              className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:opacity-90 transition"
            >
              Facts & Recall
            </Link>
            <Link
              href={`/experiments/${id}/conversation`}
              className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:opacity-90 transition"
            >
              Conversation
            </Link>
          </>
        )}
        <button
          onClick={handleDelete}
          disabled={deleting || experiment.status === "running"}
          className="ml-auto text-red-400 border border-red-400/30 px-3 py-2 rounded-md text-sm hover:bg-red-400/10 transition disabled:opacity-40"
        >
          {deleting ? "Deleting…" : "Delete"}
        </button>
      </div>

      {/* Running progress indicator */}
      {experiment.status === "running" && (
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            <p className="text-sm font-medium text-blue-400">Experiment running…</p>
          </div>
          <p className="text-xs text-muted-foreground">
            Auto-refreshing every 3 seconds. Turns completed: {experiment.total_turns} ·
            Tokens: {formatTokens(experiment.total_tokens)}
          </p>
        </div>
      )}
    </div>
  );
}

function MetaStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-semibold mt-0.5 text-sm">{value}</p>
    </div>
  );
}
