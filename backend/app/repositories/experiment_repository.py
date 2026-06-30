"""
SQLAlchemy implementation of ExperimentRepository.
Translates between ORM models and domain entities.
"""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.interfaces.experiment_repository import ExperimentRepository
from app.models.experiment import ExperimentModel


class SQLExperimentRepository(ExperimentRepository):
    """SQLAlchemy-backed experiment repository. Works with SQLite and PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, experiment: Experiment) -> Experiment:
        model = self._to_model(experiment)
        self._session.add(model)
        await self._session.flush()
        return experiment

    async def get_by_id(self, experiment_id: str) -> Experiment | None:
        result = await self._session.get(ExperimentModel, experiment_id)
        return self._to_entity(result) if result else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Experiment]:
        stmt = select(ExperimentModel).order_by(ExperimentModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    async def update_status(self, experiment_id: str, status: ExperimentStatus) -> None:
        model = await self._session.get(ExperimentModel, experiment_id)
        if model:
            model.status = status
            await self._session.flush()

    async def update(self, experiment: Experiment) -> Experiment:
        model = await self._session.get(ExperimentModel, experiment.id)
        if model:
            model.status = experiment.status
            model.error_message = experiment.error_message
            model.completed_at = experiment.completed_at
            model.started_at = experiment.started_at
            model.total_turns = experiment.total_turns
            model.total_tokens = experiment.total_tokens
            model.total_cost_usd = experiment.total_cost_usd
            await self._session.flush()
        return experiment

    async def delete(self, experiment_id: str) -> None:
        model = await self._session.get(ExperimentModel, experiment_id)
        if model:
            await self._session.delete(model)

    @staticmethod
    def _to_model(entity: Experiment) -> ExperimentModel:
        return ExperimentModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            strategy_name=entity.strategy_name,
            config=entity.config,
            status=entity.status,
            created_at=entity.created_at,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            error_message=entity.error_message,
            total_turns=entity.total_turns,
            total_tokens=entity.total_tokens,
            total_cost_usd=entity.total_cost_usd,
        )

    @staticmethod
    def _to_entity(model: ExperimentModel) -> Experiment:
        return Experiment(
            id=model.id,
            name=model.name,
            description=model.description,
            strategy_name=model.strategy_name,
            config=model.config,
            status=ExperimentStatus(model.status),
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            error_message=model.error_message,
            total_turns=model.total_turns,
            total_tokens=model.total_tokens,
            total_cost_usd=model.total_cost_usd,
        )
