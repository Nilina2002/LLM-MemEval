"""
Recall Testing Engine — full implementation.

At each recall checkpoint, asks the model to recall every fact injected so far.
The memory strategy is treated as a black box: we call retrieve() and build_context()
through the interface only — no strategy-specific logic here.
"""
from __future__ import annotations
import logging
import time
import uuid

from app.domain.entities.fact import Fact
from app.domain.entities.recall_result import RecallResult
from app.domain.interfaces.memory_strategy import MemoryStrategy
from app.domain.interfaces.llm_provider import LLMProvider
from app.evaluators.scoring.base import ScoringPipeline

logger = logging.getLogger(__name__)


class RecallTestingEngine:
    """
    Manages the when and how of recall tests.

    Design: the engine is completely strategy-agnostic. It interacts with the
    strategy only through the MemoryStrategy interface. Adding a new strategy
    requires zero changes here.
    """

    RECALL_SYSTEM_PROMPT = (
        "You are a helpful assistant. Answer the following question as precisely and "
        "concisely as possible. Use only the information available to you. "
        "If you genuinely do not know, say exactly: I don't know."
    )

    def __init__(
        self,
        llm_provider: LLMProvider,
        scoring_pipeline: ScoringPipeline,
        recall_intervals: list[int],
    ) -> None:
        self._llm = llm_provider
        self._scorer = scoring_pipeline
        self._intervals = set(recall_intervals)

    def should_test(self, turn_number: int) -> bool:
        """Return True if a recall checkpoint runs at this turn."""
        return turn_number in self._intervals

    async def run_recall_tests(
        self,
        facts: list[Fact],
        current_turn: int,
        strategy: MemoryStrategy,
        experiment_id: str,
    ) -> list[RecallResult]:
        """
        Test recall for all facts injected before current_turn.

        Args:
            facts: All facts in the experiment (includes future injections).
            current_turn: The turn number we're testing at.
            strategy: Memory strategy under evaluation (black box).
            experiment_id: For record association.

        Returns:
            RecallResult for every eligible fact.
        """
        eligible = [f for f in facts if f.insertion_turn > 0 and f.insertion_turn < current_turn]

        if not eligible:
            logger.debug("Turn %d: no eligible facts to test yet.", current_turn)
            return []

        results: list[RecallResult] = []
        for fact in eligible:
            result = await self._test_one(fact, current_turn, strategy, experiment_id)
            results.append(result)
            logger.debug(
                "Recall | turn=%d fact=%s correct=%s score=%.3f method=%s",
                current_turn, fact.fact_id[:8], result.is_correct,
                result.similarity_score, result.scoring_method,
            )

        accuracy = sum(1 for r in results if r.is_correct) / len(results) if results else 0.0
        logger.info(
            "Recall checkpoint turn=%d | %d/%d correct | accuracy=%.3f",
            current_turn, sum(1 for r in results if r.is_correct), len(results), accuracy,
        )
        return results

    async def _test_one(
        self,
        fact: Fact,
        current_turn: int,
        strategy: MemoryStrategy,
        experiment_id: str,
    ) -> RecallResult:
        """Test recall for a single fact at a single turn."""
        # 1. Ask the strategy for relevant context
        retrieved_fragments = strategy.retrieve(fact.recall_question, top_k=5)
        retrieved_context = "\n".join(retrieved_fragments) if retrieved_fragments else ""

        # 2. Build system prompt with retrieved context
        system_prompt = self.RECALL_SYSTEM_PROMPT
        if retrieved_context:
            system_prompt += f"\n\nContext from memory:\n{retrieved_context}"

        # 3. Call LLM with ONLY the recall question (not the full conversation)
        start = time.monotonic()
        try:
            llm_response = await self._llm.complete(
                system_prompt=system_prompt,
                messages=[{"role": "user", "content": fact.recall_question}],
                temperature=0.0,      # Deterministic recall answers
                max_tokens=150,       # Recall answers should be concise
            )
        except Exception as exc:
            logger.error("LLM call failed during recall test: %s", exc)
            return self._error_result(fact, current_turn, experiment_id, str(exc))

        latency_ms = (time.monotonic() - start) * 1000
        model_answer = llm_response.content.strip()

        # 4. Score the answer
        all_scores = self._scorer.score_all(fact.expected_answer, model_answer)
        best_result = self._scorer.score(fact.expected_answer, model_answer)

        # 5. Build RecallResult
        recall = RecallResult(
            id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            fact_id=fact.fact_id,
            test_turn=current_turn,
            question=fact.recall_question,
            expected_answer=fact.expected_answer,
            model_answer=model_answer,
            is_correct=best_result.is_correct,
            similarity_score=best_result.score,
            scoring_method=best_result.method,
            retrieved_context=retrieved_context,
            prompt_tokens=llm_response.prompt_tokens,
            response_tokens=llm_response.completion_tokens,
            latency_ms=latency_ms,
            cost_usd=llm_response.cost_usd,
        )
        recall.turns_since_injection = current_turn - fact.insertion_turn
        return recall

    def _error_result(
        self, fact: Fact, current_turn: int, experiment_id: str, error: str
    ) -> RecallResult:
        """Return a failed RecallResult when the LLM call errors."""
        result = RecallResult(
            id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            fact_id=fact.fact_id,
            test_turn=current_turn,
            question=fact.recall_question,
            expected_answer=fact.expected_answer,
            model_answer=f"[ERROR: {error}]",
            is_correct=False,
            similarity_score=0.0,
            scoring_method="error",
            retrieved_context="",
        )
        result.turns_since_injection = current_turn - fact.insertion_turn
        return result
