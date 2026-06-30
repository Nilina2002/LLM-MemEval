"""
Experiment Service — application-layer use cases.
Coordinates repositories and the orchestrator, returns API-ready schemas.
"""
from __future__ import annotations
import logging

from app.experiments.orchestrator import ExperimentOrchestrator
from app.core.config.experiment_config import ExperimentConfig
from app.schemas.experiment import (
    ExperimentCreateRequest,
    ExperimentResponse,
    ExperimentListResponse,
    RunExperimentResponse,
)

logger = logging.getLogger(__name__)


class ExperimentService:
    """Thin use-case layer between API endpoints and the domain orchestrator."""

    def __init__(self, orchestrator: ExperimentOrchestrator) -> None:
        self._orchestrator = orchestrator

    async def create(self, request: ExperimentCreateRequest) -> ExperimentResponse:
        experiment = await self._orchestrator.create_experiment(request.config)
        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            strategy_name=experiment.strategy_name,
            status=experiment.status.value,
            created_at=experiment.created_at,
            started_at=experiment.started_at,
            completed_at=experiment.completed_at,
            duration_seconds=experiment.duration_seconds,
            total_turns=experiment.total_turns,
            total_tokens=experiment.total_tokens,
            total_cost_usd=experiment.total_cost_usd,
        )

    async def run(self, experiment_id: str) -> RunExperimentResponse:
        await self._orchestrator.run_experiment(experiment_id)
        return RunExperimentResponse(
            experiment_id=experiment_id,
            status="running",
            message="Experiment started successfully.",
        )

    async def get(self, experiment_id: str) -> ExperimentResponse:
        experiment = await self._orchestrator.get_experiment(experiment_id)
        return ExperimentResponse(
            id=experiment.id,
            name=experiment.name,
            description=experiment.description,
            strategy_name=experiment.strategy_name,
            status=experiment.status.value,
            created_at=experiment.created_at,
            started_at=experiment.started_at,
            completed_at=experiment.completed_at,
            duration_seconds=experiment.duration_seconds,
            total_turns=experiment.total_turns,
            total_tokens=experiment.total_tokens,
            total_cost_usd=experiment.total_cost_usd,
        )

    async def delete(self, experiment_id: str) -> None:
        await self._orchestrator.delete_experiment(experiment_id)

    async def list_all(self, limit: int = 50, offset: int = 0) -> ExperimentListResponse:
        experiments = await self._orchestrator.list_experiments(limit=limit, offset=offset)
        items = [
            ExperimentResponse(
                id=e.id,
                name=e.name,
                description=e.description,
                strategy_name=e.strategy_name,
                status=e.status.value,
                created_at=e.created_at,
                started_at=e.started_at,
                completed_at=e.completed_at,
                duration_seconds=e.duration_seconds,
                total_turns=e.total_turns,
                total_tokens=e.total_tokens,
                total_cost_usd=e.total_cost_usd,
            )
            for e in experiments
        ]
        return ExperimentListResponse(
            experiments=items,
            total=len(items),
            limit=limit,
            offset=offset,
        )
