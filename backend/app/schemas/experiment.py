"""
Pydantic schemas for the Experiment API layer.
Separate from domain entities — API shape can evolve independently.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
from pydantic import BaseModel

from app.core.config.experiment_config import ExperimentConfig


class ExperimentCreateRequest(BaseModel):
    """Body of POST /experiments."""
    config: ExperimentConfig


class ExperimentResponse(BaseModel):
    """Returned by GET /experiments/{id}."""
    id: str
    name: str
    description: str
    strategy_name: str
    status: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    total_turns: int
    total_tokens: int
    total_cost_usd: float
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ExperimentListResponse(BaseModel):
    """Returned by GET /experiments."""
    experiments: list[ExperimentResponse]
    total: int
    limit: int
    offset: int


class RunExperimentResponse(BaseModel):
    """Returned by POST /experiments/{id}/run."""
    experiment_id: str
    status: str
    message: str
