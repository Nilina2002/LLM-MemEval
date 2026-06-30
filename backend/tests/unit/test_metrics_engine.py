"""Unit tests for MetricsEngine."""
from __future__ import annotations
import uuid
import pytest
from datetime import datetime

from app.metrics.engine import MetricsEngine
from app.domain.entities.recall_result import RecallResult
from app.domain.entities.fact import Fact, FactType
from app.domain.entities.metrics_snapshot import MetricsSnapshot


def _recall(fact_id: str, test_turn: int, is_correct: bool, score: float = None,
            experiment_id: str = "exp1", retrieved_context: str = "") -> RecallResult:
    r = RecallResult(
        id=str(uuid.uuid4()),
        experiment_id=experiment_id,
        fact_id=fact_id,
        test_turn=test_turn,
        question="Q",
        expected_answer="A",
        model_answer="A" if is_correct else "wrong",
        is_correct=is_correct,
        similarity_score=score if score is not None else (1.0 if is_correct else 0.0),
        scoring_method="fuzzy",
        retrieved_context=retrieved_context,
    )
    r.turns_since_injection = test_turn - 5
    return r


def _fact(fact_id: str, insertion_turn: int, importance: float = 1.0) -> Fact:
    return Fact(
        fact_id=fact_id,
        text="My name is Test.",
        expected_answer="Test",
        recall_question="What is my name?",
        insertion_turn=insertion_turn,
        fact_type=FactType.PERSONAL,
        difficulty=0.5,
        importance=importance,
    )


class TestMetricsEngine:
    def setup_method(self):
        self.engine = MetricsEngine()

    # ── memory_recall_accuracy ────────────────────────────────────────────────

    def test_accuracy_all_correct(self):
        results = [_recall("f1", 10, True), _recall("f2", 10, True)]
        assert self.engine.memory_recall_accuracy(results) == 1.0

    def test_accuracy_none_correct(self):
        results = [_recall("f1", 10, False), _recall("f2", 10, False)]
        assert self.engine.memory_recall_accuracy(results) == 0.0

    def test_accuracy_half_correct(self):
        results = [_recall("f1", 10, True), _recall("f2", 10, False)]
        assert self.engine.memory_recall_accuracy(results) == 0.5

    def test_accuracy_empty(self):
        assert self.engine.memory_recall_accuracy([]) == 0.0

    # ── information_survival_score ────────────────────────────────────────────

    def test_survival_score_single_checkpoint(self):
        results = [_recall("f1", 10, True)]
        score = self.engine._information_survival_score(results)
        assert score == 1.0

    def test_survival_score_perfect_retention(self):
        # Two checkpoints, both 100% accurate
        results = [_recall("f1", 10, True), _recall("f2", 10, True),
                   _recall("f1", 50, True), _recall("f2", 50, True)]
        score = self.engine._information_survival_score(results)
        assert abs(score - 1.0) < 0.01

    def test_survival_score_complete_forgetting(self):
        # All correct at turn 10, all wrong at turn 50
        results = [_recall("f1", 10, True), _recall("f2", 10, True),
                   _recall("f1", 50, False), _recall("f2", 50, False)]
        score = self.engine._information_survival_score(results)
        # Should be 0.5 (trapezoidal: average of 1.0 and 0.0 over the range)
        assert abs(score - 0.5) < 0.01

    def test_survival_score_empty(self):
        assert self.engine._information_survival_score([]) == 0.0

    # ── forgetting_rate ───────────────────────────────────────────────────────

    def test_forgetting_rate_zero_with_one_checkpoint(self):
        results = [_recall("f1", 10, True)]
        rate = self.engine._forgetting_rate(results, 10)
        assert rate == 0.0

    def test_forgetting_rate_negative_when_forgetting(self):
        results = [
            _recall("f1", 10, True), _recall("f2", 10, True),    # 100% at turn 10
            _recall("f1", 50, False), _recall("f2", 50, False),   # 0% at turn 50
        ]
        rate = self.engine._forgetting_rate(results, 50)
        assert rate < 0   # Negative = forgetting

    def test_forgetting_rate_positive_when_improving(self):
        results = [
            _recall("f1", 10, False), _recall("f2", 10, False),   # 0% at turn 10
            _recall("f1", 50, True), _recall("f2", 50, True),     # 100% at turn 50
        ]
        rate = self.engine._forgetting_rate(results, 50)
        assert rate > 0   # Positive = improvement

    # ── token_efficiency ──────────────────────────────────────────────────────

    def test_token_efficiency_zero_when_no_tokens(self):
        assert self.engine.token_efficiency(1.0, 0) == 0.0

    def test_token_efficiency_higher_with_fewer_tokens(self):
        eff_a = self.engine.token_efficiency(1.0, 1000)
        eff_b = self.engine.token_efficiency(1.0, 2000)
        assert eff_a > eff_b

    def test_token_efficiency_higher_with_better_accuracy(self):
        eff_a = self.engine.token_efficiency(1.0, 1000)
        eff_b = self.engine.token_efficiency(0.5, 1000)
        assert eff_a > eff_b

    # ── compute_snapshot ─────────────────────────────────────────────────────

    def test_compute_snapshot_returns_snapshot(self):
        facts = [_fact("f1", 5), _fact("f2", 7)]
        fact_map = {f.fact_id: f for f in facts}
        results_at_10 = [_recall("f1", 10, True), _recall("f2", 10, False)]
        all_results = results_at_10

        snapshot = self.engine.compute_snapshot(
            experiment_id="exp1",
            turn_number=10,
            results_at_turn=results_at_10,
            all_results_so_far=all_results,
            facts=facts,
            cumulative_tokens=1000,
            cumulative_cost=0.01,
            cumulative_latency_ms=500.0,
            result_count=2,
        )

        assert isinstance(snapshot, MetricsSnapshot)
        assert snapshot.experiment_id == "exp1"
        assert snapshot.turn_number == 10
        assert snapshot.memory_recall_accuracy == 0.5
        assert snapshot.total_tokens == 1000
        assert snapshot.total_cost_usd == pytest.approx(0.01)

    # ── experiment summary ────────────────────────────────────────────────────

    def test_experiment_summary_empty(self):
        summary = self.engine.compute_experiment_summary([])
        assert summary == {}

    def test_experiment_summary_keys(self):
        snapshot = MetricsSnapshot(
            id="s1", experiment_id="e1", turn_number=10,
            memory_recall_accuracy=0.8, long_term_recall_rate=0.6,
            information_retention_rate=0.75, forgetting_rate=-0.002,
            information_survival_score=0.85, retrieval_precision=0.9,
            retrieval_recall=0.7, context_preservation_score=0.0,
            total_tokens=1000, total_cost_usd=0.01, avg_latency_ms=200.0,
            token_efficiency=0.0008, per_fact_scores={},
        )
        summary = self.engine.compute_experiment_summary([snapshot])
        expected_keys = {
            "peak_recall_accuracy", "final_recall_accuracy", "mean_recall_accuracy",
            "information_survival_score", "total_forgetting",
            "total_tokens", "total_cost_usd", "avg_latency_ms", "token_efficiency",
        }
        assert expected_keys.issubset(summary.keys())
