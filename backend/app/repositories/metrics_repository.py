"""SQLAlchemy repository for metrics snapshots."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.models.metrics_snapshot import MetricsSnapshotModel


class SQLMetricsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, snapshot: MetricsSnapshot) -> MetricsSnapshot:
        model = self._to_model(snapshot)
        self._session.add(model)
        await self._session.flush()
        return snapshot

    async def get_by_experiment(self, experiment_id: str) -> list[MetricsSnapshot]:
        stmt = (
            select(MetricsSnapshotModel)
            .where(MetricsSnapshotModel.experiment_id == experiment_id)
            .order_by(MetricsSnapshotModel.turn_number)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars()]

    @staticmethod
    def _to_model(entity: MetricsSnapshot) -> MetricsSnapshotModel:
        return MetricsSnapshotModel(
            id=entity.id,
            experiment_id=entity.experiment_id,
            turn_number=entity.turn_number,
            memory_recall_accuracy=entity.memory_recall_accuracy,
            long_term_recall_rate=entity.long_term_recall_rate,
            information_retention_rate=entity.information_retention_rate,
            forgetting_rate=entity.forgetting_rate,
            information_survival_score=entity.information_survival_score,
            retrieval_precision=entity.retrieval_precision,
            retrieval_recall=entity.retrieval_recall,
            context_preservation_score=entity.context_preservation_score,
            total_tokens=entity.total_tokens,
            total_cost_usd=entity.total_cost_usd,
            avg_latency_ms=entity.avg_latency_ms,
            token_efficiency=entity.token_efficiency,
            per_fact_scores=entity.per_fact_scores,
            timestamp=entity.timestamp,
        )

    @staticmethod
    def _to_entity(model: MetricsSnapshotModel) -> MetricsSnapshot:
        return MetricsSnapshot(
            id=model.id,
            experiment_id=model.experiment_id,
            turn_number=model.turn_number,
            memory_recall_accuracy=model.memory_recall_accuracy,
            long_term_recall_rate=model.long_term_recall_rate,
            information_retention_rate=model.information_retention_rate,
            forgetting_rate=model.forgetting_rate,
            information_survival_score=model.information_survival_score,
            retrieval_precision=model.retrieval_precision,
            retrieval_recall=model.retrieval_recall,
            context_preservation_score=model.context_preservation_score,
            total_tokens=model.total_tokens,
            total_cost_usd=model.total_cost_usd,
            avg_latency_ms=model.avg_latency_ms,
            token_efficiency=model.token_efficiency,
            per_fact_scores=model.per_fact_scores or {},
            timestamp=model.timestamp,
        )
