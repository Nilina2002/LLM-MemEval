"""
Experiment Orchestrator.
Entry point for creating and running benchmark experiments.
Coordinates all modules without containing any business logic itself.
"""
from __future__ import annotations
import logging
import uuid

from app.core.config.experiment_config import ExperimentConfig
from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.interfaces.experiment_repository import ExperimentRepository
from app.experiments.pipeline import ExperimentPipeline
from app.strategies.registry import StrategyRegistry
from app.core.exceptions import ExperimentAlreadyRunningError, ExperimentNotFoundError

logger = logging.getLogger(__name__)


class ExperimentOrchestrator:
    """
    Coordinates experiment lifecycle: creation → validation → execution → completion.
    Uses dependency injection for all collaborators.
    """

    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        pipeline: ExperimentPipeline,
        strategy_registry: StrategyRegistry,
    ) -> None:
        self._repo = experiment_repo
        self._pipeline = pipeline
        self._registry = strategy_registry

    async def create_experiment(self, config: ExperimentConfig) -> Experiment:
        """
        Validate config and create a new experiment record.
        Does NOT start execution — call run_experiment() separately.
        """
        if not self._registry.is_registered(config.memory.strategy_name):
            from app.core.exceptions import StrategyNotFoundError
            raise StrategyNotFoundError(config.memory.strategy_name)

        experiment = Experiment(
            id=str(uuid.uuid4()),
            name=config.name,
            description=config.description,
            strategy_name=config.memory.strategy_name,
            config=config.model_dump(),
        )
        await self._repo.create(experiment)
        logger.info("Created experiment %s (strategy=%s)", experiment.id, experiment.strategy_name)
        return experiment

    async def run_experiment(self, experiment_id: str) -> None:
        """
        Start experiment execution asynchronously.
        Updates status to RUNNING, then delegates to the pipeline.
        """
        experiment = await self._repo.get_by_id(experiment_id)
        if experiment is None:
            raise ExperimentNotFoundError(experiment_id)
        if experiment.status == ExperimentStatus.RUNNING:
            raise ExperimentAlreadyRunningError(experiment_id)

        await self._repo.update_status(experiment_id, ExperimentStatus.RUNNING)
        try:
            await self._pipeline.run(experiment)
            await self._repo.update_status(experiment_id, ExperimentStatus.COMPLETED)
        except Exception as exc:
            logger.exception("Experiment %s failed: %s", experiment_id, exc)
            experiment.fail(str(exc))
            await self._repo.update(experiment)
            raise

    async def get_experiment(self, experiment_id: str) -> Experiment:
        experiment = await self._repo.get_by_id(experiment_id)
        if experiment is None:
            raise ExperimentNotFoundError(experiment_id)
        return experiment

    async def list_experiments(self, limit: int = 50, offset: int = 0) -> list[Experiment]:
        return await self._repo.list_all(limit=limit, offset=offset)
