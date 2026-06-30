"""
Scoring pipeline — orchestrates multiple scoring methods and combines results.
"""
from __future__ import annotations
from app.domain.interfaces.scorer import Scorer, ScoringResult


class ScoringPipeline:
    """
    Runs one or more scorers and returns the highest-confidence result.
    Configured by ExperimentConfig.recall.scoring_methods.
    """

    def __init__(self, scorers: list[Scorer], threshold: float = 0.8) -> None:
        self._scorers = scorers
        self._threshold = threshold

    def score(self, expected: str, actual: str) -> ScoringResult:
        """
        Score using all configured methods and return the best result.
        Primary scorer is first in list; others serve as validation/fallback.
        """
        if not self._scorers:
            return ScoringResult(score=0.0, is_correct=False, method="none")

        results = [s.score(expected, actual, self._threshold) for s in self._scorers]
        # Return the result with the highest score
        return max(results, key=lambda r: r.score)

    def score_all(self, expected: str, actual: str) -> dict[str, ScoringResult]:
        """Return results from every scorer keyed by method name."""
        return {s.method_name: s.score(expected, actual, self._threshold) for s in self._scorers}
