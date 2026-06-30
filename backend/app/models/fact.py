"""SQLAlchemy ORM model for Fact table."""
from __future__ import annotations
from sqlalchemy import String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class FactModel(Base):
    __tablename__ = "facts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    expected_answer: Mapped[str] = mapped_column(String(200), nullable=False)
    recall_question: Mapped[str] = mapped_column(String(300), nullable=False)
    insertion_turn: Mapped[int] = mapped_column(Integer, nullable=False)
    fact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    importance: Mapped[float] = mapped_column(Float, default=1.0)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    alternative_answers: Mapped[list] = mapped_column(JSON, default=list)
