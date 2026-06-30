// Dashboard home — overview of all experiments and key stats
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">LLM-MemEval</h1>
        <p className="text-muted-foreground mt-1">
          AI Forgetting Benchmark Framework — research platform for evaluating memory retention.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* TODO: replace with real data via SWR hooks */}
        <StatCard label="Total Experiments" value="—" />
        <StatCard label="Strategies Registered" value="—" />
        <StatCard label="Total API Cost" value="—" />
      </div>

      <div className="flex gap-4">
        <Link
          href="/experiments/new"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium hover:opacity-90 transition"
        >
          New Experiment
        </Link>
        <Link
          href="/experiments"
          className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md font-medium hover:opacity-90 transition"
        >
          View All Experiments
        </Link>
        <Link
          href="/compare"
          className="bg-secondary text-secondary-foreground px-4 py-2 rounded-md font-medium hover:opacity-90 transition"
        >
          Compare Strategies
        </Link>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
