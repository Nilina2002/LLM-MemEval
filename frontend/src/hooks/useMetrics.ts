// SWR hook for metrics and graph data
import useSWR from "swr";
import { getMetrics, getGraphs } from "@/lib/api";

export function useMetrics(experimentId: string | null) {
  const { data, error } = useSWR(
    experimentId ? `metrics/${experimentId}` : null,
    () => getMetrics(experimentId!)
  );
  return { metrics: data, error };
}

export function useGraphs(experimentId: string | null) {
  const { data, error } = useSWR(
    experimentId ? `graphs/${experimentId}` : null,
    () => getGraphs(experimentId!)
  );
  return { graphs: data, error };
}
