"""Unit tests for scoring pipeline and individual scorers."""
from __future__ import annotations
import pytest

from app.evaluators.scoring.exact_match import ExactMatchScorer
from app.evaluators.scoring.fuzzy_match import FuzzyMatchScorer
from app.evaluators.scoring.base import ScoringPipeline


class TestExactMatchScorer:
    def setup_method(self):
        self.scorer = ExactMatchScorer()

    def test_exact_match(self):
        result = self.scorer.score("Nilina", "Nilina")
        assert result.is_correct
        assert result.score == 1.0

    def test_case_insensitive(self):
        result = self.scorer.score("nilina", "NILINA")
        assert result.is_correct

    def test_strips_whitespace(self):
        result = self.scorer.score("Nilina", "  Nilina  ")
        assert result.is_correct

    def test_wrong_answer(self):
        result = self.scorer.score("Nilina", "James")
        assert not result.is_correct
        assert result.score == 0.0

    def test_substring_match(self):
        result = self.scorer.score("Nilina", "My name is Nilina and I'm 28.")
        assert result.is_correct

    def test_empty_answer(self):
        result = self.scorer.score("Nilina", "")
        assert not result.is_correct

    def test_method_name(self):
        assert self.scorer.method_name == "exact"


class TestFuzzyMatchScorer:
    def setup_method(self):
        self.scorer = FuzzyMatchScorer()

    def test_exact_match(self):
        result = self.scorer.score("gpt-4o-mini", "gpt-4o-mini", threshold=0.85)
        assert result.is_correct
        assert result.score == pytest.approx(1.0, abs=0.01)

    def test_near_match(self):
        # Minor typo should still score high
        result = self.scorer.score("Colombo", "Colmbo", threshold=0.8)
        assert result.score > 0.7

    def test_completely_wrong(self):
        result = self.scorer.score("Colombo", "Nairobi", threshold=0.85)
        assert not result.is_correct

    def test_method_name(self):
        assert self.scorer.method_name == "fuzzy"

    def test_threshold_respected(self):
        # Score a near-match with high threshold — should fail
        result = self.scorer.score("abc", "xyz", threshold=0.9)
        assert not result.is_correct


class TestScoringPipeline:
    def setup_method(self):
        self.pipeline = ScoringPipeline(
            [ExactMatchScorer(), FuzzyMatchScorer()],
            threshold=0.8,
        )

    def test_returns_highest_score(self):
        # Exact match scorer gives 1.0, fuzzy also high
        result = self.pipeline.score("Nilina", "Nilina")
        assert result.score == pytest.approx(1.0, abs=0.01)
        assert result.is_correct

    def test_score_all_returns_dict(self):
        results = self.pipeline.score_all("Nilina", "Nilina")
        assert "exact" in results
        assert "fuzzy" in results

    def test_uses_best_scorer(self):
        # Exact match fails but fuzzy might pass
        result = self.pipeline.score("gpt-4o-mini", "gpt4o mini")
        # Should pick the best score from either scorer
        assert result.score > 0.5

    def test_all_fail(self):
        result = self.pipeline.score("Colombo", "xyzabc123")
        assert not result.is_correct

    def test_empty_scorer_list_raises(self):
        with pytest.raises((ValueError, IndexError, Exception)):
            ScoringPipeline([], threshold=0.8).score("a", "b")
