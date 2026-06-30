"""SQLAlchemy implementation of FactRepository."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.fact import Fact, FactType
from app.domain.interfaces.fact_repository import FactRepository
from app.models.fact import FactModel


class SQLFactRepository(FactRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, facts: list[Fact]) -> list[Fact]:
        models = [self._to_model(f) for f in facts]
        self._session.add_all(models)
        await self._session.flush()
        return facts

    async def get_by_experiment(self, experiment_id: str) -> list[Fact]:
        stmt = (
            select(FactModel)
            .where(FactModel.experiment_id == experiment_id)
            .order_by(FactModel.insertion_turn)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    async def get_by_id(self, fact_id: str) -> Fact | None:
        model = await self._session.get(FactModel, fact_id)
        return self._to_entity(model) if model else None

    async def get_facts_injected_before_turn(
        self, experiment_id: str, turn: int
    ) -> list[Fact]:
        stmt = (
            select(FactModel)
            .where(
                FactModel.experiment_id == experiment_id,
                FactModel.insertion_turn < turn,
                FactModel.insertion_turn > 0,
            )
            .order_by(FactModel.insertion_turn)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    @staticmethod
    def _to_model(entity: Fact) -> FactModel:
        return FactModel(
            id=entity.fact_id,
            experiment_id="",       # Set by caller with experiment_id
            text=entity.text,
            expected_answer=entity.expected_answer,
            recall_question=entity.recall_question,
            insertion_turn=entity.insertion_turn,
            fact_type=entity.fact_type.value,
            difficulty=entity.difficulty,
            importance=entity.importance,
            tags=entity.tags,
            alternative_answers=entity.alternative_answers,
        )

    @staticmethod
    def _to_entity(model: FactModel) -> Fact:
        return Fact(
            fact_id=model.id,
            text=model.text,
            expected_answer=model.expected_answer,
            recall_question=model.recall_question,
            insertion_turn=model.insertion_turn,
            fact_type=FactType(model.fact_type),
            difficulty=model.difficulty,
            importance=model.importance,
            tags=model.tags or [],
            alternative_answers=model.alternative_answers or [],
        )


class SQLFactRepositoryWithExperiment(SQLFactRepository):
    """Variant that sets experiment_id automatically on create."""

    def __init__(self, session: AsyncSession, experiment_id: str) -> None:
        super().__init__(session)
        self._experiment_id = experiment_id

    async def create_many(self, facts: list[Fact]) -> list[Fact]:
        models = []
        for f in facts:
            m = self._to_model(f)
            m.experiment_id = self._experiment_id
            models.append(m)
        self._session.add_all(models)
        await self._session.flush()
        return facts
