"""
Strategy Registry — the plugin mechanism.

Adding a new memory strategy requires only:
  1. Implement MemoryStrategy.
  2. Call registry.register() here.
  3. Reference it by name in ExperimentConfig.memory.strategy_name.
"""
from __future__ import annotations
from typing import Any, Type

from app.domain.interfaces.memory_strategy import MemoryStrategy
from app.core.exceptions import StrategyNotFoundError


class StrategyRegistry:
    """
    Singleton registry mapping strategy names to their classes.
    The orchestrator uses this to instantiate the correct strategy at runtime.
    """

    def __init__(self) -> None:
        self._registry: dict[str, Type[MemoryStrategy]] = {}

    def register(self, strategy_class: Type[MemoryStrategy]) -> Type[MemoryStrategy]:
        """Register a strategy class. Can be used as a decorator."""
        instance = strategy_class.__new__(strategy_class)
        self._registry[instance.name] = strategy_class
        return strategy_class

    def create(self, name: str, params: dict[str, Any] | None = None) -> MemoryStrategy:
        """Instantiate a strategy by name with optional parameters."""
        if name not in self._registry:
            raise StrategyNotFoundError(name)
        cls = self._registry[name]
        return cls(**(params or {}))

    def list_strategies(self) -> list[dict[str, str]]:
        """Return metadata for all registered strategies."""
        result = []
        for name, cls in self._registry.items():
            instance = cls.__new__(cls)
            result.append({
                "name": name,
                "description": getattr(instance, "description", ""),
                "class": cls.__name__,
            })
        return result

    def is_registered(self, name: str) -> bool:
        return name in self._registry


# Global singleton — import this instance everywhere
registry = StrategyRegistry()
