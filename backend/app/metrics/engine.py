"""
Metrics Engine.
Computes all research metrics from raw RecallResult records.
Produces MetricsSnapshot objects that form the memory decay curve.
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime

from app.domain.entities.recall_result import RecallResult
from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.domain.entities.fact import Fact
from app.core.constants import LONG_TERM_THRESHOLD_TURNS, FORGETTING_RATE_WINDOW

logger = logging.getLogger(__name__)


class MetricsEngine:
    """
    Stateless computation engine. All methods are pure functions of their inputs.
    Call compute_snapshot() at each recall interval to build the decay curve.
    """

    def compute_snapshot(
        self,
        experiment_id: str,
        turn_number: int,
        results_at_turn: list[RecallResult],
        all_results_so_far: list[RecallResult],
        facts: list[Fact],
        cumulative_tokens: int,
        cumulative_cost: float,
        cumulative_latency_ms: float,
        result_count: int,
    ) -> MetricsSnapshot:
        """
        Compute all metrics for one recall checkpoint.

        Args:
            results_at_turn: RecallResults from THIS checkpoint only.
            all_results_so_far: All RecallResults from the experiment start.
        """
        # TODO: implement each metric calculation
        raise NotImplementedError

    def memory_recall_accuracy(self, results: list[RecallResult]) -> float:
        """Fraction of correct recalls at this checkpoint."""
        if not results:
            return 0.0
        return sum(1 for r in results if r.is_correct) / len(results)

    def long_term_recall_rate(self, results: list[RecallResult], facts: list[Fact]) -> float:
        """Recall accuracy for facts injected more than LONG_TERM_THRESHOLD_TURNS turns ago."""
        fact_map = {f.fact_id: f for f in facts}
        long_term = [
            r for r in results
            if (r.test_turn - fact_map[r.fact_id].insertion_turn) >= LONG_TERM_THRESHOLD_TURNS
        ]
        return self.memory_recall_accuracy(long_term)

    def forgetting_rate(self, all_snapshots: list[MetricsSnapshot]) -> float:
        """
        Rate of accuracy decay over the last FORGETTING_RATE_WINDOW turns.
        Negative values indicate forgetting; positive values indicate improvement.
        """
        if len(all_snapshots) < 2:
            return 0.0
        recent = all_snapshots[-2:]
        delta_accuracy = recent[-1].memory_recall_accuracy - recent[0].memory_recall_accuracy
        delta_turns = recent[-1].turn_number - recent[0].turn_number
        if delta_turns == 0:
            return 0.0
        return delta_accuracy / delta_turns

    def information_survival_score(self, snapshots: list[MetricsSnapshot]) -> float:
        """
        Area under the recall-vs-turn curve (trapezoidal integration).
        Higher score = information survived longer.
        """
        if len(snapshots) < 2:
            return snapshots[0].memory_recall_accuracy if snapshots else 0.0
        total_area = 0.0
        for i in range(1, len(snapshots)):
            width = snapshots[i].turn_number - snapshots[i - 1].turn_number
            avg_height = (
                snapshots[i].memory_recall_accuracy + snapshots[i - 1].memory_recall_accuracy
            ) / 2
            total_area += width * avg_height
        max_area = snapshots[-1].turn_number - snapshots[0].turn_number
        return total_area / max_area if max_area > 0 else 0.0

    def token_efficiency(self, accuracy: float, total_tokens: int) -> float:
        """Facts recalled per 1000 tokens consumed."""
        if total_tokens == 0:
            return 0.0
        return (accuracy * 1000) / total_tokens
