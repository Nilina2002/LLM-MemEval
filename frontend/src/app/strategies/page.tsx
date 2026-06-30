"use client";
import { useEffect, useState } from "react";
import { listStrategies } from "@/lib/api";
import type { Strategy } from "@/lib/types";

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);

  useEffect(() => {
    listStrategies().then(setStrategies);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Memory Strategies</h1>
      <p className="text-muted-foreground">All registered memory strategies available for benchmarking.</p>
      <div className="grid gap-3">
        {strategies.map((s) => (
          <div key={s.name} className="rounded-lg border bg-card p-4">
            <p className="font-semibold font-mono">{s.name}</p>
            <p className="text-sm text-muted-foreground mt-1">{s.description}</p>
            <p className="text-xs text-muted-foreground mt-2 opacity-60">{s.class_name}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
