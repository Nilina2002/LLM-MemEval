"""
Metrics Engine — full implementation.

All methods are pure functions of their inputs (stateless).
Produces MetricsSnapshot objects that form the memory decay curve.

Every metric is designed to answer a specific research question:
- Memory Recall Accuracy:       "What fraction of facts can the model recall right now?"
- Long-Term Recall Rate:        "How well does it remember facts from long ago?"
- Information Survival Score:   "How much information survived across the whole run?"
- Forgetting Rate:              "How fast is information being lost?"
- Token Efficiency:             "How much information did we retain per token spent?"
"""
from __future__ import annotations
import uuid
import logging
from collections import defaultdict
from datetime import datetime

from app.domain.entities.fact import Fact
from app.domain.entities.recall_result import RecallResult
from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.core.constants import LONG_TERM_THRESHOLD_TURNS

logger = logging.getLogger(__name__)


class MetricsEngine:
    """Stateless computation engine. All inputs → deterministic outputs."""

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
            results_at_turn:     Recall results from THIS checkpoint only.
            all_results_so_far:  All recall results across the full experiment.
            facts:               All facts (needed for importance weights).
            cumulative_tokens:   Total tokens used so far.
            cumulative_cost:     Total cost so far.
            cumulative_latency_ms: Cumulative latency from recall tests.
            result_count:        Number of recall tests performed so far.
        """
        fact_map = {f.fact_id: f for f in facts}

        accuracy = self.memory_recall_accuracy(results_at_turn)
        lt_recall = self.long_term_recall_rate(results_at_turn, fact_map, turn_number)
        weighted_retention = self._weighted_accuracy(results_at_turn, fact_map)
        forgetting = self._forgetting_rate(all_results_so_far, turn_number)
        survival = self._information_survival_score(all_results_so_far)
        precision = self._retrieval_precision(results_at_turn)
        recall_metric = self._retrieval_recall(results_at_turn, facts, turn_number)
        per_fact = {r.fact_id: r.similarity_score for r in results_at_turn}
        avg_latency = cumulative_latency_ms / result_count if result_count > 0 else 0.0
        token_eff = self.token_efficiency(accuracy, cumulative_tokens)

        snap = MetricsSnapshot(
            id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            turn_number=turn_number,
            memory_recall_accuracy=round(accuracy, 4),
            long_term_recall_rate=round(lt_recall, 4),
            information_retention_rate=round(weighted_retention, 4),
            forgetting_rate=round(forgetting, 6),
            information_survival_score=round(survival, 4),
            retrieval_precision=round(precision, 4),
            retrieval_recall=round(recall_metric, 4),
            context_preservation_score=0.0,     # Requires embedding — populated externally if needed
            total_tokens=cumulative_tokens,
            total_cost_usd=round(cumulative_cost, 6),
            avg_latency_ms=round(avg_latency, 2),
            token_efficiency=round(token_eff, 6),
            per_fact_scores=per_fact,
            timestamp=datetime.utcnow(),
        )
        logger.debug(
            "MetricsSnapshot | turn=%d acc=%.3f forgetting=%.4f survival=%.3f cost=$%.4f",
            turn_number, accuracy, forgetting, survival, cumulative_cost,
        )
        return snap

    # ── Core metrics ─────────────────────────────────────────────────────────

    def memory_recall_accuracy(self, results: list[RecallResult]) -> float:
        """Fraction of correct recalls at this checkpoint. Range: [0, 1]."""
        if not results:
            return 0.0
        return sum(1 for r in results if r.is_correct) / len(results)

    def long_term_recall_rate(
        self,
        results: list[RecallResult],
        fact_map: dict[str, Fact],
        current_turn: int,
    ) -> float:
        """
        Recall accuracy for facts injected more than LONG_TERM_THRESHOLD_TURNS ago.
        Tests genuinely long-term memory, not short-term retention.
        """
        long_term = [
            r for r in results
            if r.fact_id in fact_map
            and (current_turn - fact_map[r.fact_id].insertion_turn) >= LONG_TERM_THRESHOLD_TURNS
        ]
        return self.memory_recall_accuracy(long_term)

    def token_efficiency(self, accuracy: float, total_tokens: int) -> float:
        """
        Information retained per 1000 tokens consumed.
        Higher = the strategy retains more per token spent.
        """
        if total_tokens == 0:
            return 0.0
        return (accuracy * 1000) / total_tokens

    # ── Forgetting metrics ────────────────────────────────────────────────────

    def _forgetting_rate(
        self,
        all_results: list[RecallResult],
        current_turn: int,
    ) -> float:
        """
        Rate of accuracy change between the last two checkpoints.
        Negative = forgetting; positive = improvement; 0 = stable.
        """
        # Group results by test_turn
        by_turn: dict[int, list[RecallResult]] = defaultdict(list)
        for r in all_results:
            by_turn[r.test_turn].append(r)

        sorted_turns = sorted(by_turn.keys())
        if len(sorted_turns) < 2:
            return 0.0

        prev_turn = sorted_turns[-2]
        last_turn = sorted_turns[-1]
        prev_acc = self.memory_recall_accuracy(by_turn[prev_turn])
        last_acc = self.memory_recall_accuracy(by_turn[last_turn])
        delta_turns = last_turn - prev_turn
        if delta_turns == 0:
            return 0.0
        return (last_acc - prev_acc) / delta_turns

    def _information_survival_score(self, all_results: list[RecallResult]) -> float:
        """
        Area under the recall-accuracy-vs-turn curve (trapezoidal integration).
        Normalised to [0, 1]. Higher = information survived more of the conversation.

        This is the primary single-number research metric for comparing strategies.
        """
        by_turn: dict[int, list[RecallResult]] = defaultdict(list)
        for r in all_results:
            by_turn[r.test_turn].append(r)

        sorted_turns = sorted(by_turn.keys())
        if len(sorted_turns) < 2:
            if sorted_turns:
                return self.memory_recall_accuracy(by_turn[sorted_turns[0]])
            return 0.0

        accuracies = [self.memory_recall_accuracy(by_turn[t]) for t in sorted_turns]

        total_area = 0.0
        for i in range(1, len(sorted_turns)):
            width = sorted_turns[i] - sorted_turns[i - 1]
            avg_height = (accuracies[i] + accuracies[i - 1]) / 2.0
            total_area += width * avg_height

        max_area = sorted_turns[-1] - sorted_turns[0]
        return total_area / max_area if max_area > 0 else accuracies[-1]

    # ── Weighted metrics ──────────────────────────────────────────────────────

    def _weighted_accuracy(
        self,
        results: list[RecallResult],
        fact_map: dict[str, Fact],
    ) -> float:
        """
        Accuracy weighted by fact importance.
        Important facts (importance=1.0) contribute more to this score.
        """
        if not results:
            return 0.0
        total_weight = 0.0
        weighted_correct = 0.0
        for r in results:
            importance = fact_map[r.fact_id].importance if r.fact_id in fact_map else 1.0
            total_weight += importance
            if r.is_correct:
                weighted_correct += importance
        return weighted_correct / total_weight if total_weight > 0 else 0.0

    # ── Retrieval quality ─────────────────────────────────────────────────────

    def _retrieval_precision(self, results: list[RecallResult]) -> float:
        """
        Fraction of queries where the retrieved context contained useful information.
        Proxy: if retrieved_context is non-empty AND the answer was correct.
        """
        if not results:
            return 0.0
        with_context = [r for r in results if r.retrieved_context.strip()]
        if not with_context:
            return 0.0
        return sum(1 for r in with_context if r.is_correct) / len(with_context)

    def _retrieval_recall(
        self,
        results: list[RecallResult],
        facts: list[Fact],
        current_turn: int,
    ) -> float:
        """
        Fraction of injected facts for which the strategy retrieved something.
        Measures coverage of the memory strategy's retrieval.
        """
        if not results:
            return 0.0
        retrieved_count = sum(1 for r in results if r.retrieved_context.strip())
        return retrieved_count / len(results)

    # ── Summary stats ─────────────────────────────────────────────────────────

    def compute_experiment_summary(
        self, snapshots: list[MetricsSnapshot]
    ) -> dict[str, float]:
        """
        Compute experiment-level summary statistics from all snapshots.
        Used in the comparison dashboard and result export.
        """
        if not snapshots:
            return {}

        accuracies = [s.memory_recall_accuracy for s in snapshots]
        return {
            "peak_recall_accuracy":       max(accuracies),
            "final_recall_accuracy":      accuracies[-1],
            "mean_recall_accuracy":       sum(accuracies) / len(accuracies),
            "information_survival_score": snapshots[-1].information_survival_score,
            "total_forgetting":           accuracies[0] - accuracies[-1] if len(accuracies) > 1 else 0.0,
            "total_tokens":               float(snapshots[-1].total_tokens),
            "total_cost_usd":             snapshots[-1].total_cost_usd,
            "avg_latency_ms":             snapshots[-1].avg_latency_ms,
            "token_efficiency":           snapshots[-1].token_efficiency,
        }
