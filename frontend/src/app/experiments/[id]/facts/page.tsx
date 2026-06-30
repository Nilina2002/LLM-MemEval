"use client";
import { useParams } from "next/navigation";

export default function FactsPage() {
  const { id } = useParams<{ id: string }>();
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Fact Injection Viewer</h1>
      <p className="text-muted-foreground">Experiment: {id}</p>
      {/* TODO: FactCard list + FactTimeline heatmap */}
    </div>
  );
}
