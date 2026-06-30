"""SQLAlchemy ORM model for MetricsSnapshot table."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class MetricsSnapshotModel(Base):
    __tablename__ = "metrics_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_recall_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    long_term_recall_rate: Mapped[float] = mapped_column(Float, default=0.0)
    information_retention_rate: Mapped[float] = mapped_column(Float, default=0.0)
    forgetting_rate: Mapped[float] = mapped_column(Float, default=0.0)
    information_survival_score: Mapped[float] = mapped_column(Float, default=0.0)
    retrieval_precision: Mapped[float] = mapped_column(Float, default=0.0)
    retrieval_recall: Mapped[float] = mapped_column(Float, default=0.0)
    context_preservation_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    token_efficiency: Mapped[float] = mapped_column(Float, default=0.0)
    per_fact_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
