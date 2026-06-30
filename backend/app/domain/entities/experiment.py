"""
Domain entity: Experiment.
Pure Python dataclass — no framework dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExperimentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Experiment:
    """
    Represents a single benchmark experiment run.
    Owns its configuration and tracks lifecycle state.
    """
    id: str
    name: str
    description: str
    strategy_name: str
    config: dict[str, Any]
    status: ExperimentStatus = ExperimentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    total_turns: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0

    def start(self) -> None:
        """Transition experiment to running state."""
        self.status = ExperimentStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        """Transition experiment to completed state."""
        self.status = ExperimentStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        """Transition experiment to failed state with error message."""
        self.status = ExperimentStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
