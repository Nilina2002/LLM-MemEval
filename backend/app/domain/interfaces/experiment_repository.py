"""
Abstract repository for Experiment persistence.
Separates domain logic from storage implementation (SQLite or PostgreSQL).
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from app.domain.entities.experiment import Experiment, ExperimentStatus


class ExperimentRepository(ABC):
    """Repository interface for Experiment entities."""

    @abstractmethod
    async def create(self, experiment: Experiment) -> Experiment:
        ...

    @abstractmethod
    async def get_by_id(self, experiment_id: str) -> Experiment | None:
        ...

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Experiment]:
        ...

    @abstractmethod
    async def update_status(self, experiment_id: str, status: ExperimentStatus) -> None:
        ...

    @abstractmethod
    async def update(self, experiment: Experiment) -> Experiment:
        ...

    @abstractmethod
    async def delete(self, experiment_id: str) -> None:
        ...
