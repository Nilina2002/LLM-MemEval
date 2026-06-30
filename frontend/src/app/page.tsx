"use client";
import Link from "next/link";
import useSWR from "swr";
import { listExperiments, listStrategies } from "@/lib/api";
import { formatCost, formatTokens } from "@/lib/utils";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { FlaskConical, Brain, DollarSign, CheckCircle } from "lucide-react";

export default function HomePage() {
  const { data: expData } = useSWR("experiments-overview", () => listExperiments(200, 0));
  const { data: strategies } = useSWR("strategies-list", listStrategies);

  const experiments = expData?.experiments ?? [];
  const completed = experiments.filter((e) => e.status === "completed");
  const totalCost = experiments.reduce((s, e) => s + (e.total_cost_usd ?? 0), 0);
  const totalTokens = experiments.reduce((s, e) => s + (e.total_tokens ?? 0), 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">LLM-MemEval</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          AI Forgetting Benchmark Framework — scientific evaluation of LLM memory retention.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={FlaskConical}
          label="Total Experiments"
          value={expData ? String(experiments.length) : "—"}
          sub={expData ? `${completed.length} completed` : undefined}
        />
        <StatCard
          icon={Brain}
          label="Strategies"
          value={strategies ? String(strategies.length) : "—"}
          sub="registered"
        />
        <StatCard
          icon={DollarSign}
          label="Total API Cost"
          value={expData ? formatCost(totalCost) : "—"}
          sub={expData ? `${formatTokens(totalTokens)} tokens` : undefined}
        />
        <StatCard
          icon={CheckCircle}
          label="Completed Runs"
          value={expData ? String(completed.length) : "—"}
          sub={
            expData && experiments.length > 0
              ? `${Math.round((completed.length / experiments.length) * 100)}% success rate`
              : undefined
          }
        />
      </div>

      {/* Quick actions */}
      <div className="flex gap-3 flex-wrap">
        <Link
          href="/experiments/new"
          className="bg-primary text-primary-foreground px-5 py-2.5 rounded-md text-sm font-medium hover:opacity-90 transition"
        >
          + New Experiment
        </Link>
        <Link
          href="/experiments"
          className="bg-secondary text-secondary-foreground px-5 py-2.5 rounded-md text-sm font-medium hover:opacity-90 transition"
        >
          All Experiments
        </Link>
        <Link
          href="/compare"
          className="bg-secondary text-secondary-foreground px-5 py-2.5 rounded-md text-sm font-medium hover:opacity-90 transition"
        >
          Compare Strategies
        </Link>
      </div>

      {/* Recent experiments */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Recent Experiments</h2>
        {!expData ? (
          <LoadingSpinner />
        ) : experiments.length === 0 ? (
          <p className="text-sm text-muted-foreground py-4">
            No experiments yet.{" "}
            <Link href="/experiments/new" className="text-primary hover:underline">
              Create your first one.
            </Link>
          </p>
        ) : (
          <div className="space-y-2">
            {experiments.slice(0, 5).map((exp) => (
              <Link
                key={exp.id}
                href={`/experiments/${exp.id}`}
                className="flex items-center justify-between rounded-lg border bg-card p-3 hover:border-primary/40 transition"
              >
                <div>
                  <p className="text-sm font-medium">{exp.name}</p>
                  <p className="text-xs text-muted-foreground">{exp.strategy_name}</p>
                </div>
                <div className="text-right text-xs text-muted-foreground">
                  <p
                    className={
                      exp.status === "completed"
                        ? "text-green-400"
                        : exp.status === "running"
                        ? "text-blue-400"
                        : exp.status === "failed"
                        ? "text-red-400"
                        : "text-yellow-400"
                    }
                  >
                    {exp.status}
                  </p>
                  <p>{formatCost(exp.total_cost_usd)}</p>
                </div>
              </Link>
            ))}
            {experiments.length > 5 && (
              <Link href="/experiments" className="text-xs text-primary hover:underline block pt-1">
                View all {experiments.length} experiments →
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4 space-y-1">
      <div className="flex items-center gap-2 text-muted-foreground">
        <Icon size={14} />
        <p className="text-xs">{label}</p>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
    </div>
  );
}
