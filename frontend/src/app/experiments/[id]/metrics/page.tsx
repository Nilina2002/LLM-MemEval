"use client";
import { useParams } from "next/navigation";
// Metrics & charts page — full implementation in Step 6

export default function MetricsPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Metrics & Charts</h1>
      <p className="text-muted-foreground">Experiment ID: {id}</p>
      {/* TODO: MetricsGrid + DecayCurve + FactTimeline charts */}
      <div className="rounded-lg border bg-card p-6 text-center text-muted-foreground h-64">
        Memory Decay Curve — implemented in Step 6
      </div>
    </div>
  );
}
