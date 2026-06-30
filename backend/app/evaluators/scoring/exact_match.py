"""Exact match scorer — case-insensitive string equality."""
from __future__ import annotations
from app.domain.interfaces.scorer import Scorer, ScoringResult


class ExactMatchScorer(Scorer):
    @property
    def method_name(self) -> str:
        return "exact"

    def score(self, expected: str, actual: str, threshold: float = 1.0) -> ScoringResult:
        expected_norm = expected.strip().lower()
        actual_norm = actual.strip().lower()
        is_match = expected_norm == actual_norm or expected_norm in actual_norm
        score = 1.0 if is_match else 0.0
        return ScoringResult(
            score=score,
            is_correct=score >= threshold,
            method=self.method_name,
            explanation=f"Expected '{expected}', got '{actual}'.",
        )
