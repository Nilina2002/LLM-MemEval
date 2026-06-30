"""
Domain entity: MetricsSnapshot.
A point-in-time measurement of all metrics at a given turn.
Snapshots are collected at every recall interval to build the decay curve.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricsSnapshot:
    """
    All computed metrics at a single recall checkpoint.

    A sequence of MetricsSnapshots over the conversation
    produces the memory decay curve — the primary research output.
    """
    id: str
    experiment_id: str
    turn_number: int

    # --- Recall Metrics ---
    memory_recall_accuracy: float           # Correct / total facts tested
    long_term_recall_rate: float            # Accuracy for facts injected >500 turns ago
    information_retention_rate: float       # Weighted by fact importance

    # --- Forgetting Metrics ---
    forgetting_rate: float                  # Δ(accuracy) / Δ(turns)  [negative = forgetting]
    information_survival_score: float       # AUC of recall curve up to this turn

    # --- Retrieval Quality ---
    retrieval_precision: float              # Relevant retrieved / total retrieved
    retrieval_recall: float                 # Relevant retrieved / total relevant
    context_preservation_score: float      # Embedding similarity: retrieved vs. original fact

    # --- Resource Metrics ---
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    token_efficiency: float = 0.0          # Facts recalled per 1000 tokens consumed

    # --- Per-Fact Breakdown ---
    per_fact_scores: dict[str, float] = field(default_factory=dict)   # fact_id → score

    timestamp: datetime = field(default_factory=datetime.utcnow)
