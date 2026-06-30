// Core domain types mirroring backend entities.
// Keep in sync with backend Pydantic schemas.

export type ExperimentStatus = "pending" | "running" | "completed" | "failed" | "cancelled";

export interface Experiment {
  id: string;
  name: string;
  description: string;
  strategy_name: string;
  status: ExperimentStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  total_turns: number;
  total_tokens: number;
  total_cost_usd: number;
  error_message: string | null;
}

export interface Fact {
  id: string;
  experiment_id: string;
  text: string;
  expected_answer: string;
  recall_question: string;
  insertion_turn: number;
  fact_type: string;
  difficulty: number;
  importance: number;
}

export interface Message {
  id: string;
  experiment_id: string;
  turn_number: number;
  role: "system" | "user" | "assistant";
  content: string;
  tokens: number;
  timestamp: string;
  contains_injected_fact: boolean;
  fact_id: string | null;
}

export interface RecallResult {
  id: string;
  experiment_id: string;
  fact_id: string;
  test_turn: number;
  question: string;
  expected_answer: string;
  model_answer: string;
  is_correct: boolean;
  similarity_score: number;
  scoring_method: string;
}

export interface MetricsSnapshot {
  turn_number: number;
  memory_recall_accuracy: number;
  long_term_recall_rate: number;
  forgetting_rate: number;
  information_survival_score: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  token_efficiency: number;
  timestamp: string;
}

export interface Strategy {
  name: string;
  description: string;
  class_name: string;
}

export interface PlotlyFigure {
  data: unknown[];
  layout: Record<string, unknown>;
}

// Config types for experiment creation form
export interface ExperimentCreatePayload {
  config: {
    name: string;
    description: string;
    llm: {
      provider: string;
      model: string;
      temperature: number;
      max_tokens: number;
      base_url?: string;
    };
    conversation: {
      domain: string;
      total_turns: number;
      seed: number;
    };
    facts: {
      count: number;
      types: string[];
      injection_strategy: string;
      seed?: number;
    };
    memory: {
      strategy_name: string;
      strategy_params: Record<string, unknown>;
    };
    recall: {
      intervals: number[];
      scoring_methods: string[];
    };
  };
}
