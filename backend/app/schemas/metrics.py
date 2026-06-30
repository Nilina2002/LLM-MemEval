"""Pydantic schemas for metrics API responses."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class MetricsSnapshotResponse(BaseModel):
    turn_number: int
    memory_recall_accuracy: float
    long_term_recall_rate: float
    forgetting_rate: float
    information_survival_score: float
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    token_efficiency: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class ExperimentMetricsResponse(BaseModel):
    experiment_id: str
    strategy_name: str
    snapshots: list[MetricsSnapshotResponse]
    summary: dict[str, float]   # peak accuracy, final accuracy, ISS, etc.


class CompareExperimentsRequest(BaseModel):
    experiment_ids: list[str]


class CompareExperimentsResponse(BaseModel):
    experiments: list[dict]
    comparison_chart: dict   # Plotly JSON
