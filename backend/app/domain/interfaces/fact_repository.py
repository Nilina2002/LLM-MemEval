"""
Abstract repository for Fact persistence.
"""
from __future__ import annotations
from abc import ABC, abstractmethod

from app.domain.entities.fact import Fact


class FactRepository(ABC):
    """Repository interface for Fact entities."""

    @abstractmethod
    async def create_many(self, facts: list[Fact]) -> list[Fact]:
        ...

    @abstractmethod
    async def get_by_experiment(self, experiment_id: str) -> list[Fact]:
        ...

    @abstractmethod
    async def get_by_id(self, fact_id: str) -> Fact | None:
        ...

    @abstractmethod
    async def get_facts_injected_before_turn(
        self, experiment_id: str, turn: int
    ) -> list[Fact]:
        ...
