"use client";
import Link from "next/link";
import useSWR from "swr";
import { listExperiments } from "@/lib/api";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatTokens, formatCost } from "@/lib/utils";

export default function ExperimentsPage() {
  const { data, error } = useSWR("experiments-list", () => listExperiments(100, 0));

  if (error) return <div className="text-sm text-red-400 py-8">Failed to load experiments.</div>;

  const experiments = data?.experiments ?? [];

  return (
    <div className="space-y-4 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Experiments</h1>
          {data && (
            <p className="text-muted-foreground text-sm">{data.total} total</p>
          )}
        </div>
        <Link
          href="/experiments/new"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:opacity-90 transition"
        >
          + New
        </Link>
      </div>

      {!data ? (
        <LoadingSpinner />
      ) : experiments.length === 0 ? (
        <EmptyState
          title="No experiments yet"
          message="Create your first benchmark experiment."
          action={
            <Link href="/experiments/new" className="text-sm text-primary hover:underline">
              Create experiment →
            </Link>
          }
        />
      ) : (
        <div className="space-y-2">
          {experiments.map((exp) => (
            <Link
              key={exp.id}
              href={`/experiments/${exp.id}`}
              className="block rounded-lg border bg-card p-4 hover:border-primary/40 transition"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium truncate">{exp.name}</p>
                  <p className="text-sm text-muted-foreground">{exp.strategy_name}</p>
                  {exp.description && (
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{exp.description}</p>
                  )}
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <StatusBadge status={exp.status} />
                  <p className="text-xs text-muted-foreground">
                    {formatTokens(exp.total_tokens)} · {formatCost(exp.total_cost_usd)}
                  </p>
                  {exp.created_at && (
                    <p className="text-xs text-muted-foreground/60">
                      {new Date(exp.created_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
