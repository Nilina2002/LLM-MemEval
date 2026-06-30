// SWR hook for experiment data with auto-polling while running
import useSWR from "swr";
import { getExperiment, getExperimentStatus } from "@/lib/api";
import type { Experiment } from "@/lib/types";

export function useExperiment(id: string | null) {
  const { data, error, mutate } = useSWR<Experiment>(
    id ? `experiments/${id}` : null,
    () => getExperiment(id!),
    {
      refreshInterval: (data) =>
        data?.status === "running" ? 3000 : 0, // poll every 3s while running
    }
  );

  return { experiment: data, error, refresh: mutate };
}

export function useExperimentStatus(id: string | null) {
  const { data } = useSWR(
    id ? `experiments/${id}/status` : null,
    () => getExperimentStatus(id!),
    { refreshInterval: 2000 }
  );
  return data;
}
