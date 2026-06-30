import { cn } from "@/lib/utils";
import type { ExperimentStatus } from "@/lib/types";

const styles: Record<string, string> = {
  pending:   "bg-yellow-400/15 text-yellow-400 border-yellow-400/30",
  running:   "bg-blue-400/15 text-blue-400 border-blue-400/30",
  completed: "bg-green-400/15 text-green-400 border-green-400/30",
  failed:    "bg-red-400/15 text-red-400 border-red-400/30",
  cancelled: "bg-gray-400/15 text-gray-400 border-gray-400/30",
};

export function StatusBadge({ status }: { status: ExperimentStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        styles[status] ?? styles.cancelled
      )}
    >
      {status === "running" && (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
      )}
      {status}
    </span>
  );
}
