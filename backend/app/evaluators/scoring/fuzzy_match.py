"""
Fuzzy match scorer using rapidfuzz.
Handles typos, partial answers, and minor variations.
"""
from __future__ import annotations
from app.domain.interfaces.scorer import Scorer, ScoringResult


class FuzzyMatchScorer(Scorer):
    @property
    def method_name(self) -> str:
        return "fuzzy"

    def score(self, expected: str, actual: str, threshold: float = 0.85) -> ScoringResult:
        try:
            from rapidfuzz import fuzz
            ratio = fuzz.partial_ratio(expected.lower(), actual.lower()) / 100.0
        except ImportError:
            # Graceful fallback to exact match if rapidfuzz not installed
            ratio = 1.0 if expected.strip().lower() in actual.strip().lower() else 0.0

        return ScoringResult(
            score=ratio,
            is_correct=ratio >= threshold,
            method=self.method_name,
            explanation=f"Fuzzy ratio: {ratio:.3f} (threshold: {threshold})",
        )
