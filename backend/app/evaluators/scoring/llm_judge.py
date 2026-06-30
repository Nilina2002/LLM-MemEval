"""
LLM Judge scorer.
Uses a separate LLM call to determine semantic correctness.
Most accurate but most expensive — use selectively on difficult facts.
"""
from __future__ import annotations
from app.domain.interfaces.scorer import Scorer, ScoringResult
from app.domain.interfaces.llm_provider import LLMProvider


JUDGE_PROMPT = """You are an objective evaluator.
Determine if the MODEL ANSWER correctly answers the QUESTION given the EXPECTED ANSWER.

QUESTION: {question}
EXPECTED ANSWER: {expected}
MODEL ANSWER: {actual}

Respond with ONLY a JSON object: {{"correct": true/false, "score": 0.0-1.0, "reason": "..."}}
"""


class LLMJudgeScorer(Scorer):
    """
    Asks an LLM to judge correctness. Captures semantic equivalence
    that fuzzy matching and embeddings may miss (e.g., "Nissan Tiida" vs "a Tiida").
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    @property
    def method_name(self) -> str:
        return "llm_judge"

    def score(self, expected: str, actual: str, threshold: float = 0.8) -> ScoringResult:
        # LLM judge requires async — this sync version is a blocking wrapper
        # In the pipeline, call score_async() instead
        import asyncio
        return asyncio.run(self.score_async(expected, actual, threshold))

    async def score_async(
        self, expected: str, actual: str, threshold: float = 0.8, question: str = ""
    ) -> ScoringResult:
        """Async version for use in the evaluation pipeline."""
        # TODO: implement — call self._llm.complete() with JUDGE_PROMPT, parse JSON response
        raise NotImplementedError
