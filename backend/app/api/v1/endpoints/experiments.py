"""
Experiments API endpoints.
"""
from __future__ import annotations
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db

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
) -> RunExperimentResponse:
    """Start experiment execution as a background task."""
    background_tasks.add_task(_run_experiment_task, experiment_id)
    return RunExperimentResponse(
        experiment_id=experiment_id,
        status="running",
        message="Experiment queued for execution.",
    )


async def _run_experiment_task(experiment_id: str) -> None:
    """Background task — builds its own session so it doesn't share with the HTTP request."""
    from app.api.dependencies import get_experiment_service
    async for service in get_experiment_service():
        try:
            await service._orchestrator.run_experiment(experiment_id)
        except Exception as exc:
            logger.exception("Background run failed for %s: %s", experiment_id, exc)


@router.get("/{experiment_id}/facts")
async def get_facts(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return all facts injected into this experiment."""
    from app.repositories.fact_repository import SQLFactRepository
    repo = SQLFactRepository(db)
    facts = await repo.get_by_experiment(experiment_id)
    return [
        {
            "id": f.fact_id,
            "experiment_id": experiment_id,
            "text": f.text,
            "expected_answer": f.expected_answer,
            "recall_question": f.recall_question,
            "insertion_turn": f.insertion_turn,
            "fact_type": f.fact_type.value,
            "difficulty": f.difficulty,
            "importance": f.importance,
            "tags": f.tags,
        }
        for f in facts
    ]


@router.get("/{experiment_id}/recall")
async def get_recall_results(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Return all recall test results for this experiment."""
    from app.repositories.recall_repository import SQLRecallRepository
    repo = SQLRecallRepository(db)
    results = await repo.get_by_experiment(experiment_id)
    return [
        {
            "id": r.id,
            "fact_id": r.fact_id,
            "test_turn": r.test_turn,
            "question": r.question,
            "expected_answer": r.expected_answer,
            "model_answer": r.model_answer,
            "is_correct": r.is_correct,
            "similarity_score": r.similarity_score,
            "scoring_method": r.scoring_method,
            "latency_ms": r.latency_ms,
            "cost_usd": r.cost_usd,
        }
        for r in results
    ]


@router.get("/{experiment_id}/conversation")
async def get_conversation(
    experiment_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return paginated conversation messages."""
    from app.repositories.message_repository import SQLMessageRepository
    repo = SQLMessageRepository(db)
    offset = (page - 1) * page_size
    messages = await repo.get_by_experiment(experiment_id, limit=page_size, offset=offset)
    total = await repo.count_by_experiment(experiment_id)
    return {
        "messages": [
            {
                "id": m.id,
                "experiment_id": m.experiment_id,
                "turn_number": m.turn_number,
                "role": m.role.value,
                "content": m.content,
                "tokens": m.tokens,
                "timestamp": m.timestamp.isoformat(),
                "contains_injected_fact": m.contains_injected_fact,
                "fact_id": m.fact_id,
                "latency_ms": m.latency_ms,
                "cost_usd": m.cost_usd,
            }
            for m in messages
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: str,
    service: ExperimentService = Depends(get_experiment_service),
) -> None:
    """Delete an experiment and all associated data."""
    try:
        await service.delete(experiment_id)
    except ExperimentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


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
