"""
Experiments API endpoints.
"""
from __future__ import annotations
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.schemas.experiment import (
    ExperimentCreateRequest,
    ExperimentListResponse,
    ExperimentResponse,
    RunExperimentResponse,
)
from app.services.experiment_service import ExperimentService
from app.api.dependencies import get_experiment_service
from app.core.exceptions import (
    ExperimentNotFoundError,
    ExperimentAlreadyRunningError,
    StrategyNotFoundError,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    request: ExperimentCreateRequest,
    service: ExperimentService = Depends(get_experiment_service),
) -> ExperimentResponse:
    """Create a new experiment configuration. Does not start execution."""
    try:
        return await service.create(request)
    except StrategyNotFoundError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("", response_model=ExperimentListResponse)
async def list_experiments(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    service: ExperimentService = Depends(get_experiment_service),
) -> ExperimentListResponse:
    """List all experiments, newest first."""
    return await service.list_all(limit=limit, offset=offset)


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: str,
    service: ExperimentService = Depends(get_experiment_service),
) -> ExperimentResponse:
    """Get a single experiment by ID."""
    try:
        return await service.get(experiment_id)
    except ExperimentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{experiment_id}/run", response_model=RunExperimentResponse)
async def run_experiment(
    experiment_id: str,
    background_tasks: BackgroundTasks,
    service: ExperimentService = Depends(get_experiment_service),
) -> RunExperimentResponse:
    """Start experiment execution as a background task."""
    try:
        background_tasks.add_task(service.run, experiment_id)
        return RunExperimentResponse(
            experiment_id=experiment_id,
            status="running",
            message="Experiment queued for execution.",
        )
    except ExperimentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ExperimentAlreadyRunningError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/{experiment_id}/status")
async def get_experiment_status(
    experiment_id: str,
    service: ExperimentService = Depends(get_experiment_service),
) -> dict:
    """Poll experiment status — for frontend progress tracking."""
    try:
        experiment = await service.get(experiment_id)
        return {
            "experiment_id": experiment_id,
            "status": experiment.status,
            "total_turns": experiment.total_turns,
            "total_tokens": experiment.total_tokens,
            "total_cost_usd": experiment.total_cost_usd,
        }
    except ExperimentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
