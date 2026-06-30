"""Metrics and graphs API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.metrics import (
    ExperimentMetricsResponse,
    CompareExperimentsRequest,
    CompareExperimentsResponse,
)
from app.api.dependencies import get_experiment_service
from app.core.exceptions import ExperimentNotFoundError

router = APIRouter(tags=["metrics"])


@router.get("/experiments/{experiment_id}/metrics", response_model=ExperimentMetricsResponse)
async def get_metrics(
    experiment_id: str,
    service=Depends(get_experiment_service),
) -> ExperimentMetricsResponse:
    """Return all metrics snapshots for an experiment."""
    # TODO: implement via MetricsService
    raise HTTPException(status_code=501, detail="Not yet implemented.")


@router.get("/experiments/{experiment_id}/graphs")
async def get_graphs(experiment_id: str) -> dict:
    """Return Plotly figure JSON for all standard charts."""
    # TODO: implement via VisualizationEngine
    raise HTTPException(status_code=501, detail="Not yet implemented.")


@router.post("/compare", response_model=CompareExperimentsResponse)
async def compare_experiments(request: CompareExperimentsRequest) -> CompareExperimentsResponse:
    """Compare metrics across multiple experiments with overlay chart."""
    # TODO: implement via ComparisonService
    raise HTTPException(status_code=501, detail="Not yet implemented.")
