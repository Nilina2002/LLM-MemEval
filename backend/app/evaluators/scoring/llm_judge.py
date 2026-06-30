"""
LLM Judge Scorer — full async implementation.
Uses a separate LLM call to determine correctness with natural language reasoning.
"""
from __future__ import annotations
import json
import logging
from app.domain.interfaces.scorer import Scorer, ScoringResult
from app.domain.interfaces.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

JUDGE_SYSTEM = "You are an objective evaluator. Respond ONLY with valid JSON. No explanation outside the JSON."

JUDGE_PROMPT = """Evaluate whether the MODEL ANSWER correctly answers the QUESTION, given the EXPECTED ANSWER.

QUESTION: {question}
EXPECTED ANSWER: {expected}
MODEL ANSWER: {actual}

Rules:
- Minor phrasing differences are acceptable if the meaning is the same.
- Partial answers that contain the key information count as correct.
- "I don't know" or equivalent = incorrect.
- Extra information beyond the answer is fine.

Respond with ONLY this JSON:
{{"correct": true_or_false, "score": 0.0_to_1.0, "reason": "one sentence"}}"""


class LLMJudgeScorer(Scorer):
    """
    LLM-as-a-judge scorer. Most accurate for complex, open-ended recall answers.
    Use selectively — each call costs tokens and time.
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    @property
    def method_name(self) -> str:
        return "llm_judge"

    def score(self, expected: str, actual: str, threshold: float = 0.8) -> ScoringResult:
        """Blocking wrapper — use score_async() in async contexts."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In an async context; return a partial result and warn
                logger.warning("LLMJudgeScorer.score() called from async context. Use score_async().")
                return ScoringResult(score=0.0, is_correct=False, method=self.method_name,
                                     explanation="Use score_async() in async contexts.")
            return loop.run_until_complete(
                self.score_async(expected, actual, threshold, question="")
            )
        except Exception as exc:
            logger.error("LLM judge error: %s", exc)
            return ScoringResult(score=0.0, is_correct=False, method=self.method_name,
                                 explanation=f"Error: {exc}")

    async def score_async(
        self,
        expected: str,
        actual: str,
        threshold: float = 0.8,
        question: str = "",
    ) -> ScoringResult:
        """
        Async judge evaluation.

        Args:
            expected: Ground truth answer.
            actual: Model's response to the recall question.
            threshold: Minimum score to be considered correct.
            question: The original recall question (improves judge accuracy).
        """
        prompt = JUDGE_PROMPT.format(
            question=question or "Does the answer match?",
            expected=expected,
            actual=actual,
        )

        try:
            response = await self._llm.complete(
                system_prompt=JUDGE_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,       # Deterministic judging
                max_tokens=150,
            )

            raw = response.content.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            parsed = json.loads(raw)
            score = float(parsed.get("score", 0.0))
            correct = bool(parsed.get("correct", False))
            reason = str(parsed.get("reason", ""))

            # Reconcile: if score >= threshold but correct is False, trust score
            is_correct = correct or score >= threshold

            return ScoringResult(
                score=score,
                is_correct=is_correct,
                method=self.method_name,
                explanation=reason,
            )

        except json.JSONDecodeError as exc:
            logger.warning("LLM judge returned non-JSON: %s | raw: %s", exc, response.content[:200])
            # Fallback: do simple substring check
            fallback_correct = expected.lower().strip() in actual.lower().strip()
            return ScoringResult(
                score=1.0 if fallback_correct else 0.0,
                is_correct=fallback_correct,
                method=self.method_name,
                explanation=f"JSON parse failed; used substring fallback. Raw: {response.content[:100]}",
            )

        except Exception as exc:
            logger.error("LLM judge failed: %s", exc)
            return ScoringResult(
                score=0.0,
                is_correct=False,
                method=self.method_name,
                explanation=f"Judge error: {exc}",
            )
