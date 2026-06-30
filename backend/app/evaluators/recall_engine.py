"""
Recall Testing Engine.
Manages the when and how of recall tests during an experiment run.
Completely decoupled from the memory strategy under test.
"""
from __future__ import annotations
import logging

from app.domain.entities.fact import Fact
from app.domain.entities.recall_result import RecallResult
from app.domain.interfaces.memory_strategy import MemoryStrategy
from app.domain.interfaces.llm_provider import LLMProvider
from app.evaluators.scoring.base import ScoringPipeline

logger = logging.getLogger(__name__)


class RecallTestingEngine:
    """
    At each recall interval, asks the LLM to recall every fact injected so far.
    The strategy under test provides context — the engine measures the outcome.

    The engine is completely strategy-agnostic: it calls strategy.retrieve()
    and strategy.build_context() through the interface only.
    """

    RECALL_SYSTEM_PROMPT = (
        "You are a helpful assistant. Answer the following question as concisely as possible. "
        "If you don't know the answer, say 'I don't know.'"
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
        """Return True if a recall test should run at this turn."""
        return turn_number in self._intervals

    async def run_recall_tests(
        self,
        facts: list[Fact],
        current_turn: int,
        strategy: MemoryStrategy,
        experiment_id: str,
    ) -> list[RecallResult]:
        """
        Run recall tests for all facts injected before current_turn.

        Args:
            facts: All facts in the experiment.
            current_turn: The turn at which we're testing.
            strategy: The memory strategy under evaluation (treated as black box).
            experiment_id: For logging/DB association.

        Returns:
            List of RecallResults, one per eligible fact.
        """
        eligible_facts = [f for f in facts if f.insertion_turn < current_turn]
        results = []
        for fact in eligible_facts:
            result = await self._test_single_fact(
                fact, current_turn, strategy, experiment_id
            )
            results.append(result)
            logger.debug(
                "Recall test | turn=%d fact=%s correct=%s score=%.3f",
                current_turn, fact.fact_id, result.is_correct, result.similarity_score,
            )
        return results

    async def _test_single_fact(
        self,
        fact: Fact,
        current_turn: int,
        strategy: MemoryStrategy,
        experiment_id: str,
    ) -> RecallResult:
        """Ask the model to recall one fact and score the answer."""
        # TODO: implement
        #   1. Call strategy.retrieve(fact.recall_question) to get retrieved context
        #   2. Build prompt with retrieved context + recall question
        #   3. Call self._llm.complete()
        #   4. Score response with self._scorer.score()
        #   5. Build and return RecallResult
        raise NotImplementedError
