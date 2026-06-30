"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { listExperiments } from "@/lib/api";
import type { Experiment } from "@/lib/types";
import { statusColor, formatTokens, formatCost } from "@/lib/utils";

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listExperiments()
      .then((res) => setExperiments(res.experiments))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Experiments</h1>
        <Link
          href="/experiments/new"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium"
        >
          + New Experiment
        </Link>
      </div>

      {loading && <p className="text-muted-foreground">Loading…</p>}

      <div className="space-y-2">
        {experiments.map((exp) => (
          <Link key={exp.id} href={`/experiments/${exp.id}`}>
            <div className="rounded-lg border bg-card p-4 hover:border-primary/50 transition cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{exp.name}</p>
                  <p className="text-sm text-muted-foreground">{exp.strategy_name}</p>
                </div>
                <div className="text-right text-sm">
                  <p className={statusColor(exp.status)}>{exp.status}</p>
                  <p className="text-muted-foreground">
                    {formatTokens(exp.total_tokens)} tokens · {formatCost(exp.total_cost_usd)}
                  </p>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
