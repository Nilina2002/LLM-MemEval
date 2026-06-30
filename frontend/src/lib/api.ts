// API client — all backend calls go through here.
// Endpoint path is the single source of truth.

import axios from "axios";
import type {
  Experiment,
  ExperimentCreatePayload,
  MetricsSnapshot,
  Strategy,
  PlotlyFigure,
  Fact,
  RecallResult,
  Message,
} from "./types";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// --- Experiments ---

export async function createExperiment(payload: ExperimentCreatePayload): Promise<Experiment> {
  const { data } = await api.post<Experiment>("/experiments", payload);
  return data;
}

export async function listExperiments(limit = 50, offset = 0): Promise<{
  experiments: Experiment[];
  total: number;
}> {
  const { data } = await api.get("/experiments", { params: { limit, offset } });
  return data;
}

export async function getExperiment(id: string): Promise<Experiment> {
  const { data } = await api.get<Experiment>(`/experiments/${id}`);
  return data;
}

export async function runExperiment(id: string): Promise<{ status: string; message: string }> {
  const { data } = await api.post(`/experiments/${id}/run`);
  return data;
}

export async function getExperimentStatus(id: string): Promise<{
  status: string;
  total_turns: number;
  total_tokens: number;
  total_cost_usd: number;
}> {
  const { data } = await api.get(`/experiments/${id}/status`);
  return data;
}

// --- Metrics ---

export async function getMetrics(experimentId: string): Promise<{
  snapshots: MetricsSnapshot[];
  summary: Record<string, number>;
}> {
  const { data } = await api.get(`/experiments/${experimentId}/metrics`);
  return data;
}

export async function getGraphs(experimentId: string): Promise<Record<string, PlotlyFigure>> {
  const { data } = await api.get(`/experiments/${experimentId}/graphs`);
  return data;
}

// --- Facts ---

export async function getFacts(experimentId: string): Promise<Fact[]> {
  const { data } = await api.get(`/experiments/${experimentId}/facts`);
  return data;
}

// --- Conversation ---

export async function getConversation(
  experimentId: string,
  page = 1,
  pageSize = 50
): Promise<{ messages: Message[]; total: number }> {
  const { data } = await api.get(`/experiments/${experimentId}/conversation`, {
    params: { page, page_size: pageSize },
  });
  return data;
}

// --- Strategies ---

export async function listStrategies(): Promise<Strategy[]> {
  const { data } = await api.get<{ strategies: Strategy[] }>("/strategies");
  return data.strategies;
}

// --- Compare ---

export async function compareExperiments(
  experimentIds: string[]
): Promise<{ experiments: Experiment[]; comparison_chart: PlotlyFigure }> {
  const { data } = await api.post("/compare", { experiment_ids: experimentIds });
  return data;
}
