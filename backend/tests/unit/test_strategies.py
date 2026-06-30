"""Unit tests for memory strategies."""
from __future__ import annotations
import uuid
import pytest
from datetime import datetime

from app.strategies.no_memory import NoMemoryStrategy
from app.strategies.sliding_window import SlidingWindowStrategy
from app.domain.entities.message import Message, MessageRole


def _msg(role: str, content: str, turn: int = 1) -> Message:
    return Message(
        id=str(uuid.uuid4()),
        experiment_id="exp1",
        turn_number=turn,
        role=MessageRole(role),
        content=content,
        timestamp=datetime.utcnow(),
    )


class TestNoMemoryStrategy:
    def setup_method(self):
        self.strategy = NoMemoryStrategy()

    def test_name(self):
        assert self.strategy.name == "no_memory"

    def test_build_context_returns_empty(self):
        messages = [_msg("user", "Hello"), _msg("assistant", "Hi")]
        assert self.strategy.build_context(messages) == ""

    def test_retrieve_returns_empty(self):
        assert self.strategy.retrieve("anything") == []

    def test_update_is_noop(self):
        msg = _msg("user", "hello")
        # Should not raise
        self.strategy.update_memory(msg)

    def test_clear_is_noop(self):
        # Should not raise
        self.strategy.clear()

    def test_memory_stats_returns_dict(self):
        stats = self.strategy.get_memory_stats()
        assert isinstance(stats, dict)


class TestSlidingWindowStrategy:
    def setup_method(self):
        self.strategy = SlidingWindowStrategy(window_size=4)

    def test_name(self):
        assert "sliding" in self.strategy.name.lower() or "window" in self.strategy.name.lower()

    def test_empty_context_initially(self):
        context = self.strategy.build_context([])
        assert context == ""

    def test_build_context_after_messages(self):
        m1 = _msg("user", "Hello", 1)
        m2 = _msg("assistant", "Hi there", 1)
        self.strategy.update_memory(m1)
        self.strategy.update_memory(m2)
        context = self.strategy.build_context([])
        assert "Hello" in context
        assert "Hi there" in context

    def test_window_limits_messages(self):
        strategy = SlidingWindowStrategy(window_size=2)
        for i in range(6):
            strategy.update_memory(_msg("user", f"Message {i}", i))
        context = strategy.build_context([])
        # Only last 2 messages should appear
        assert "Message 5" in context
        assert "Message 4" in context
        assert "Message 0" not in context

    def test_clear_resets_memory(self):
        m = _msg("user", "Important info")
        self.strategy.update_memory(m)
        self.strategy.clear()
        context = self.strategy.build_context([])
        assert "Important info" not in context

    def test_retrieve_returns_recent(self):
        for i in range(5):
            self.strategy.update_memory(_msg("user", f"fact number {i}", i))
        results = self.strategy.retrieve("fact")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_memory_stats(self):
        msg = _msg("user", "test")
        self.strategy.update_memory(msg)
        stats = self.strategy.get_memory_stats()
        assert "window_size" in stats or "message_count" in stats or isinstance(stats, dict)


class TestStrategyRegistry:
    def test_no_memory_registered(self):
        from app.strategies.registry import registry
        from app.strategies import register_all_strategies
        register_all_strategies()
        assert registry.is_registered("no_memory")

    def test_sliding_window_registered(self):
        from app.strategies.registry import registry
        from app.strategies import register_all_strategies
        register_all_strategies()
        assert registry.is_registered("sliding_window")

    def test_create_no_memory(self):
        from app.strategies.registry import registry
        from app.strategies import register_all_strategies
        register_all_strategies()
        strategy = registry.create("no_memory", {})
        assert strategy.name == "no_memory"

    def test_create_sliding_window(self):
        from app.strategies.registry import registry
        from app.strategies import register_all_strategies
        register_all_strategies()
        strategy = registry.create("sliding_window", {"window_size": 5})
        assert strategy is not None

    def test_unknown_strategy_raises(self):
        from app.strategies.registry import registry
        from app.core.exceptions import StrategyNotFoundError
        with pytest.raises(StrategyNotFoundError):
            registry.create("nonexistent_strategy_xyz", {})

    def test_list_strategies(self):
        from app.strategies.registry import registry
        from app.strategies import register_all_strategies
        register_all_strategies()
        strategies = registry.list_strategies()
        assert len(strategies) >= 2
        names = [s["name"] for s in strategies]
        assert "no_memory" in names
        assert "sliding_window" in names
