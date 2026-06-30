"""SQLAlchemy ORM model for RecallResult table."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class RecallResultModel(Base):
    __tablename__ = "recall_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("facts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_turn: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    expected_answer: Mapped[str] = mapped_column(String(200), nullable=False)
    model_answer: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    scoring_method: Mapped[str] = mapped_column(String(50), nullable=False)
    retrieved_context: Mapped[str] = mapped_column(String(5000), default="")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    response_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
