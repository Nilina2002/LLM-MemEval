"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getExperiment, runExperiment } from "@/lib/api";
import type { Experiment } from "@/lib/types";
import { statusColor, formatTokens, formatCost } from "@/lib/utils";

export default function ExperimentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [experiment, setExperiment] = useState<Experiment | null>(null);

  useEffect(() => {
    if (id) getExperiment(id).then(setExperiment);
  }, [id]);

  if (!experiment) return <p className="text-muted-foreground">Loading…</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{experiment.name}</h1>
          <p className="text-muted-foreground">{experiment.description}</p>
        </div>
        <span className={`text-sm font-medium ${statusColor(experiment.status)}`}>
          {experiment.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetaStat label="Strategy" value={experiment.strategy_name} />
        <MetaStat label="Turns" value={String(experiment.total_turns)} />
        <MetaStat label="Tokens" value={formatTokens(experiment.total_tokens)} />
        <MetaStat label="Cost" value={formatCost(experiment.total_cost_usd)} />
      </div>

      <div className="flex gap-3">
        {experiment.status === "pending" && (
          <button
            onClick={() => runExperiment(experiment.id)}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium"
          >
            Run Experiment
          </button>
        )}
        <Link href={`/experiments/${id}/metrics`} className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm">
          Metrics & Charts
        </Link>
        <Link href={`/experiments/${id}/conversation`} className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm">
          Conversation
        </Link>
        <Link href={`/experiments/${id}/facts`} className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm">
          Facts
        </Link>
      </div>
    </div>
  );
}

function MetaStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-semibold mt-0.5">{value}</p>
    </div>
  );
}
