"""SQLAlchemy repository for recall results."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.recall_result import RecallResult
from app.models.recall_result import RecallResultModel


class SQLRecallRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, results: list[RecallResult]) -> list[RecallResult]:
        models = [self._to_model(r) for r in results]
        self._session.add_all(models)
        await self._session.flush()
        return results

    async def get_by_experiment(self, experiment_id: str) -> list[RecallResult]:
        stmt = (
            select(RecallResultModel)
            .where(RecallResultModel.experiment_id == experiment_id)
            .order_by(RecallResultModel.test_turn, RecallResultModel.fact_id)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    async def get_by_turn(
        self, experiment_id: str, test_turn: int
    ) -> list[RecallResult]:
        stmt = (
            select(RecallResultModel)
            .where(
                RecallResultModel.experiment_id == experiment_id,
                RecallResultModel.test_turn == test_turn,
            )
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    @staticmethod
    def _to_model(entity: RecallResult) -> RecallResultModel:
        return RecallResultModel(
            id=entity.id,
            experiment_id=entity.experiment_id,
            fact_id=entity.fact_id,
            test_turn=entity.test_turn,
            question=entity.question,
            expected_answer=entity.expected_answer,
            model_answer=entity.model_answer,
            is_correct=entity.is_correct,
            similarity_score=entity.similarity_score,
            scoring_method=entity.scoring_method,
            retrieved_context=entity.retrieved_context[:5000],  # Truncate to column limit
            prompt_tokens=entity.prompt_tokens,
            response_tokens=entity.response_tokens,
            latency_ms=entity.latency_ms,
            cost_usd=entity.cost_usd,
            timestamp=entity.timestamp,
        )

    @staticmethod
    def _to_entity(model: RecallResultModel) -> RecallResult:
        result = RecallResult(
            id=model.id,
            experiment_id=model.experiment_id,
            fact_id=model.fact_id,
            test_turn=model.test_turn,
            question=model.question,
            expected_answer=model.expected_answer,
            model_answer=model.model_answer,
            is_correct=model.is_correct,
            similarity_score=model.similarity_score,
            scoring_method=model.scoring_method,
            retrieved_context=model.retrieved_context,
            prompt_tokens=model.prompt_tokens,
            response_tokens=model.response_tokens,
            latency_ms=model.latency_ms,
            cost_usd=model.cost_usd,
            timestamp=model.timestamp,
        )
        return result
