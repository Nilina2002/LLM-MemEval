"""
Experiment Pipeline — the main execution loop.

This is the heart of the benchmark. Every experiment flows through here.
The pipeline contains ZERO memory-strategy-specific logic. It interacts with
the strategy exclusively through the MemoryStrategy interface.

Turn loop per experiment:
  1. Take the pre-generated user message.
  2. Ask the strategy for context (build_context).
  3. Send system_prompt + context + user_message to LLM.
  4. Record the LLM's response.
  5. Feed both messages to the strategy (update_memory).
  6. Log everything to DB and JSONL files.
  7. At recall intervals: run recall tests → compute metrics → log snapshot.

After all turns: generate visualizations and finalize experiment.
"""
from __future__ import annotations
import logging
import time
import uuid
from datetime import datetime

from app.domain.entities.experiment import Experiment
from app.domain.entities.message import Message, MessageRole
from app.domain.entities.recall_result import RecallResult
from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.domain.interfaces.memory_strategy import MemoryStrategy
from app.domain.interfaces.llm_provider import LLMProvider, LLMResponse
from app.evaluators.recall_engine import RecallTestingEngine
from app.evaluators.scoring.base import ScoringPipeline
from app.evaluators.scoring.fuzzy_match import FuzzyMatchScorer
from app.evaluators.scoring.embedding_similarity import EmbeddingSimilarityScorer
from app.generators.conversation_generator import ConversationGenerator, GeneratedConversation
from app.generators.fact_injector import FactInjector
from app.metrics.engine import MetricsEngine
from app.logger.experiment_logger import ExperimentLogger
from app.repositories.fact_repository import SQLFactRepositoryWithExperiment
from app.repositories.message_repository import SQLMessageRepository
from app.repositories.recall_repository import SQLRecallRepository
from app.repositories.metrics_repository import SQLMetricsRepository
from app.strategies.registry import StrategyRegistry
from app.core.config.experiment_config import ExperimentConfig
from app.visualization.engine import VisualizationEngine

logger = logging.getLogger(__name__)


class ExperimentPipeline:
    """
    Executes one experiment end-to-end.
    Constructed via dependency injection — all collaborators passed at init time.
    """

    BASE_SYSTEM_PROMPT = (
        "You are a helpful, friendly assistant engaged in a natural conversation. "
        "Be concise and conversational. Do not summarize what was said before — "
        "just continue the conversation naturally."
    )

    def __init__(
        self,
        llm_provider: LLMProvider,
        strategy_registry: StrategyRegistry,
        exp_logger: ExperimentLogger,
        metrics_engine: MetricsEngine,
        viz_engine: VisualizationEngine,
        db_session,                   # AsyncSession — typed weakly to avoid circular import
    ) -> None:
        self._llm = llm_provider
        self._registry = strategy_registry
        self._logger = exp_logger
        self._metrics = metrics_engine
        self._viz = viz_engine
        self._db = db_session

    async def run(self, experiment: Experiment) -> None:
        """
        Execute one complete experiment.
        Called by ExperimentOrchestrator after status is set to RUNNING.
        """
        config = ExperimentConfig.model_validate(experiment.config)

        # ── Repositories ──────────────────────────────────────────────────────
        fact_repo = SQLFactRepositoryWithExperiment(self._db, experiment.id)
        msg_repo = SQLMessageRepository(self._db)
        recall_repo = SQLRecallRepository(self._db)
        metrics_repo = SQLMetricsRepository(self._db)

        # ── Instantiate strategy ──────────────────────────────────────────────
        strategy: MemoryStrategy = self._registry.create(
            config.memory.strategy_name,
            config.memory.strategy_params,
        )
        strategy.clear()
        logger.info(
            "Experiment %s: using strategy '%s'", experiment.id[:8], strategy.name
        )

        # ── Build scoring pipeline ────────────────────────────────────────────
        scorers = self._build_scorers(config)
        scoring_pipeline = ScoringPipeline(scorers, threshold=config.recall.scoring_threshold)

        # ── Build recall engine ───────────────────────────────────────────────
        recall_engine = RecallTestingEngine(
            llm_provider=self._llm,
            scoring_pipeline=scoring_pipeline,
            recall_intervals=config.recall.intervals,
        )

        # ── Generate conversation ─────────────────────────────────────────────
        conv_generator = ConversationGenerator()
        fact_injector = FactInjector()

        facts_raw = fact_injector.generate_facts(config.facts)
        injection_positions = conv_generator.calculate_injection_positions(
            total_turns=config.conversation.total_turns,
            fact_count=len(facts_raw),
            strategy=config.facts.injection_strategy,
            seed=config.facts.seed,
        )
        conversation = conv_generator.generate(config.conversation, injection_positions)
        conversation, facts = fact_injector.inject_into_conversation(conversation, facts_raw)

        # ── Persist facts ─────────────────────────────────────────────────────
        await fact_repo.create_many(facts)
        await self._logger.log_config(experiment.id, experiment.config)
        await self._logger.log_facts(experiment.id, facts)
        logger.info("Generated %d facts for experiment %s", len(facts), experiment.id[:8])

        # ── Main turn loop ────────────────────────────────────────────────────
        all_messages: list[Message] = []
        all_recall_results: list[RecallResult] = []
        all_snapshots: list[MetricsSnapshot] = []
        cumulative_tokens = 0
        cumulative_cost = 0.0
        cumulative_latency = 0.0
        recall_test_count = 0

        for turn in conversation.turns:
            turn_start = time.monotonic()
            user_content = turn.user_message

            # Build context from strategy's current memory state
            context = strategy.build_context(all_messages, query=user_content)
            system_prompt = self._build_system_prompt(context)

            # Format conversation history for the LLM call
            history = self._format_history(all_messages, max_turns=5)

            # Call LLM
            try:
                llm_response = await self._llm.complete(
                    system_prompt=system_prompt,
                    messages=history + [{"role": "user", "content": user_content}],
                    temperature=config.llm.temperature,
                    max_tokens=config.llm.max_tokens,
                )
            except Exception as exc:
                logger.error("LLM failed at turn %d: %s", turn.turn_number, exc)
                # Continue with a dummy response rather than aborting the experiment
                llm_response = LLMResponse(
                    content="[LLM error — continuing]",
                    prompt_tokens=0, completion_tokens=0, total_tokens=0,
                    model="error", latency_ms=0.0, cost_usd=0.0,
                )

            # Create message entities
            fact_at_turn = next(
                (f for f in facts if f.insertion_turn == turn.turn_number), None
            )
            user_msg = Message(
                id=str(uuid.uuid4()),
                experiment_id=experiment.id,
                turn_number=turn.turn_number,
                role=MessageRole.USER,
                content=user_content,
                tokens=llm_response.prompt_tokens,
                timestamp=datetime.utcnow(),
                contains_injected_fact=fact_at_turn is not None,
                fact_id=fact_at_turn.fact_id if fact_at_turn else None,
            )
            assistant_msg = Message(
                id=str(uuid.uuid4()),
                experiment_id=experiment.id,
                turn_number=turn.turn_number,
                role=MessageRole.ASSISTANT,
                content=llm_response.content,
                tokens=llm_response.completion_tokens,
                timestamp=datetime.utcnow(),
                latency_ms=llm_response.latency_ms,
                cost_usd=llm_response.cost_usd,
            )

            # Update strategy with new messages
            strategy.update_memory(user_msg)
            strategy.update_memory(assistant_msg)
            all_messages.extend([user_msg, assistant_msg])

            # Persist messages
            await msg_repo.create_many([user_msg, assistant_msg])

            # Update cumulative stats
            cumulative_tokens += llm_response.total_tokens
            cumulative_cost += llm_response.cost_usd

            # Log to JSONL
            await self._logger.log_turn(experiment.id, user_msg, assistant_msg, llm_response)

            # ── Recall checkpoint ─────────────────────────────────────────────
            if recall_engine.should_test(turn.turn_number):
                recall_results = await recall_engine.run_recall_tests(
                    facts=facts,
                    current_turn=turn.turn_number,
                    strategy=strategy,
                    experiment_id=experiment.id,
                )

                if recall_results:
                    all_recall_results.extend(recall_results)
                    recall_test_count += len(recall_results)
                    cumulative_latency += sum(r.latency_ms for r in recall_results)

                    # Persist recall results
                    await recall_repo.create_many(recall_results)
                    for r in recall_results:
                        await self._logger.log_recall_result(r)

                    # Compute metrics snapshot
                    snapshot = self._metrics.compute_snapshot(
                        experiment_id=experiment.id,
                        turn_number=turn.turn_number,
                        results_at_turn=recall_results,
                        all_results_so_far=all_recall_results,
                        facts=facts,
                        cumulative_tokens=cumulative_tokens,
                        cumulative_cost=cumulative_cost,
                        cumulative_latency_ms=cumulative_latency,
                        result_count=recall_test_count,
                    )
                    all_snapshots.append(snapshot)
                    await metrics_repo.create(snapshot)
                    await self._logger.log_metrics_snapshot(snapshot)

                    logger.info(
                        "Turn %d | acc=%.3f | forgetting=%.4f | tokens=%d | cost=$%.4f",
                        turn.turn_number,
                        snapshot.memory_recall_accuracy,
                        snapshot.forgetting_rate,
                        cumulative_tokens,
                        cumulative_cost,
                    )

        # ── Finalize experiment ───────────────────────────────────────────────
        experiment.total_turns = len(conversation.turns)
        experiment.total_tokens = cumulative_tokens
        experiment.total_cost_usd = cumulative_cost
        logger.info(
            "Experiment %s complete | turns=%d | tokens=%d | cost=$%.4f",
            experiment.id[:8], experiment.total_turns, cumulative_tokens, cumulative_cost,
        )

    def _build_system_prompt(self, memory_context: str) -> str:
        if memory_context:
            return f"{self.BASE_SYSTEM_PROMPT}\n\n{memory_context}"
        return self.BASE_SYSTEM_PROMPT

    @staticmethod
    def _format_history(
        messages: list[Message],
        max_turns: int = 5,
    ) -> list[dict[str, str]]:
        """
        Format the last max_turns pairs as OpenAI-style messages.
        We only pass a short recent history to the LLM — the strategy provides
        the rest as context in the system prompt.
        """
        recent = messages[-(max_turns * 2):]
        return [{"role": m.role.value, "content": m.content} for m in recent]

    @staticmethod
    def _build_scorers(config: ExperimentConfig):
        """Build scorer list from config."""
        scorers = []
        for method in config.recall.scoring_methods:
            if method == "exact":
                from app.evaluators.scoring.exact_match import ExactMatchScorer
                scorers.append(ExactMatchScorer())
            elif method == "fuzzy":
                scorers.append(FuzzyMatchScorer())
            elif method == "embedding":
                scorers.append(EmbeddingSimilarityScorer())
            # llm_judge requires an LLM provider — added by the pipeline if configured
        if not scorers:
            scorers.append(FuzzyMatchScorer())   # Safe default
        return scorers
