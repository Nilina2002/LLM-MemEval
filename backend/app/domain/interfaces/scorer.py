"""
Abstract interface for all scoring methods.
Scoring methods evaluate whether a model's recall answer is correct.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScoringResult:
    """Output of a single scoring evaluation."""
    score: float            # 0.0 (wrong) → 1.0 (perfect)
    is_correct: bool        # score >= threshold
    method: str             # scoring method name
    explanation: str = ""   # human-readable reason (especially useful for LLM judge)


class Scorer(ABC):
    """
    Abstract scorer. Implementations: ExactMatch, FuzzyMatch,
    EmbeddingSimilarity, LLMJudge.
    """

    @property
    @abstractmethod
    def method_name(self) -> str:
        """Identifier for this scoring method."""
        ...

    @abstractmethod
    def score(
        self,
        expected: str,
        actual: str,
        threshold: float = 0.8,
    ) -> ScoringResult:
        """
        Score a model's answer against the expected answer.

        Args:
            expected: Ground truth answer.
            actual: Model's response.
            threshold: Minimum score to consider correct.

        Returns:
            ScoringResult with score, correctness flag, and explanation.
        """
        ...
