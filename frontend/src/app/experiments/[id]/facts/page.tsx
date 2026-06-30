"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import { getFacts, getRecallResults } from "@/lib/api";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { formatPercent } from "@/lib/utils";

export default function FactsPage() {
  const { id } = useParams<{ id: string }>();

  const { data: facts, error: factsErr } = useSWR(
    id ? `facts/${id}` : null,
    () => getFacts(id!)
  );
  const { data: recalls } = useSWR(
    id ? `recall/${id}` : null,
    () => getRecallResults(id!)
  );

  if (factsErr) return <div className="text-sm text-red-400 py-8">Failed to load facts.</div>;
  if (!facts) return <LoadingSpinner label="Loading facts…" />;

  if (facts.length === 0) {
    return (
      <EmptyState
        title="No facts yet"
        message="Facts are generated when the experiment runs."
        action={
          <Link href={`/experiments/${id}`} className="text-sm text-primary hover:underline">
            ← Back
          </Link>
        }
      />
    );
  }

  // Build per-fact recall summary
  const recallByFact: Record<string, { correct: number; total: number; scores: number[] }> = {};
  for (const r of recalls ?? []) {
    if (!recallByFact[r.fact_id]) recallByFact[r.fact_id] = { correct: 0, total: 0, scores: [] };
    recallByFact[r.fact_id].total++;
    if (r.is_correct) recallByFact[r.fact_id].correct++;
    recallByFact[r.fact_id].scores.push(r.similarity_score);
  }

  const totalRecalls = recalls?.length ?? 0;
  const correctRecalls = recalls?.filter((r) => r.is_correct).length ?? 0;

  return (
    <div className="space-y-5 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Facts & Recall</h1>
          <p className="text-muted-foreground text-sm">
            {facts.length} injected facts · {totalRecalls} recall tests
          </p>
        </div>
        <Link href={`/experiments/${id}`} className="text-sm text-muted-foreground hover:text-foreground">
          ← Experiment
        </Link>
      </div>

      {/* Overall recall rate banner */}
      {totalRecalls > 0 && (
        <div className="rounded-lg border bg-card px-4 py-3 text-sm">
          Overall recall accuracy:{" "}
          <span className="font-bold text-foreground">
            {formatPercent(correctRecalls / totalRecalls)}
          </span>
          {" "}({correctRecalls}/{totalRecalls} correct across all checkpoints)
        </div>
      )}

      <div className="rounded-lg border overflow-x-auto">
        <table className="w-full text-sm min-w-[700px]">
          <thead className="bg-secondary/50">
            <tr>
              {["#", "Text", "Question", "Expected Answer", "Type", "Turn", "Recall Rate", "Avg Score"].map((h) => (
                <th key={h} className="px-3 py-2 text-left text-xs text-muted-foreground font-medium whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {facts.map((fact, i) => {
              const stat = recallByFact[fact.id];
              const recallRate = stat ? stat.correct / stat.total : null;
              const avgScore =
                stat ? stat.scores.reduce((a, b) => a + b, 0) / stat.scores.length : null;

              return (
                <tr key={fact.id} className="hover:bg-secondary/20 transition align-top">
                  <td className="px-3 py-2.5 text-muted-foreground text-xs">{i + 1}</td>
                  <td className="px-3 py-2.5 max-w-[200px]">
                    <p className="text-xs line-clamp-3">{fact.text}</p>
                  </td>
                  <td className="px-3 py-2.5 max-w-[180px]">
                    <p className="text-xs text-muted-foreground line-clamp-2">{fact.recall_question}</p>
                  </td>
                  <td className="px-3 py-2.5">
                    <span className="font-mono text-xs bg-secondary px-1.5 py-0.5 rounded">
                      {fact.expected_answer}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-xs text-muted-foreground whitespace-nowrap">
                    {fact.fact_type}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-xs">
                    {fact.insertion_turn || "—"}
                  </td>
                  <td className="px-3 py-2.5">
                    {recallRate !== null ? (
                      <span className={recallRate >= 0.5 ? "text-green-400" : "text-red-400"}>
                        {formatPercent(recallRate)}{" "}
                        <span className="text-muted-foreground text-xs">
                          ({stat?.correct}/{stat?.total})
                        </span>
                      </span>
                    ) : (
                      <span className="text-muted-foreground text-xs">—</span>
                    )}
                  </td>
                  <td className="px-3 py-2.5">
                    {avgScore !== null ? (
                      <span className="text-xs font-mono">{avgScore.toFixed(3)}</span>
                    ) : (
                      <span className="text-muted-foreground text-xs">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
