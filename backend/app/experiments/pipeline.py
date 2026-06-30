"""
Experiment Pipeline.
The main execution loop: turn by turn, fact by fact, metric by metric.
This is the heart of the benchmark — but it contains zero memory-strategy-specific logic.
"""
from __future__ import annotations
import logging

from app.domain.entities.experiment import Experiment
from app.domain.entities.message import Message, MessageRole
from app.domain.interfaces.memory_strategy import MemoryStrategy
from app.domain.interfaces.llm_provider import LLMProvider
from app.domain.interfaces.fact_repository import FactRepository
from app.evaluators.recall_engine import RecallTestingEngine
from app.metrics.engine import MetricsEngine
from app.logger.experiment_logger import ExperimentLogger
from app.strategies.registry import StrategyRegistry
from app.core.config.experiment_config import ExperimentConfig

logger = logging.getLogger(__name__)


class ExperimentPipeline:
    """
    Executes one complete experiment from start to finish.

    Turn loop:
      1. Build prompt (system + memory_context + current_turn)
      2. Call LLM → get response
      3. Call strategy.update_memory(new_message)
      4. Log turn
      5. If turn in recall_intervals → run recall tests → compute metrics
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        recall_engine: RecallTestingEngine,
        metrics_engine: MetricsEngine,
        experiment_logger: ExperimentLogger,
        fact_repo: FactRepository,
        strategy_registry: StrategyRegistry,
    ) -> None:
        self._llm = llm_provider
        self._recall_engine = recall_engine
        self._metrics_engine = metrics_engine
        self._logger = experiment_logger
        self._fact_repo = fact_repo
        self._registry = strategy_registry

    async def run(self, experiment: Experiment) -> None:
        """Execute the full experiment turn loop."""
        config = ExperimentConfig.model_validate(experiment.config)
        strategy: MemoryStrategy = self._registry.create(
            config.memory.strategy_name, config.memory.strategy_params
        )
        strategy.clear()

        facts = await self._fact_repo.get_by_experiment(experiment.id)
        all_recall_results = []
        all_snapshots = []
        cumulative_tokens = 0
        cumulative_cost = 0.0

        conversation_turns = await self._load_conversation_turns(experiment.id)

        for turn_number, (user_msg_content, _) in enumerate(conversation_turns, start=1):
            # --- Build context from strategy ---
            context = strategy.build_context(
                messages=[], query=user_msg_content  # strategy receives full history via update_memory
            )

            # --- Construct and send prompt ---
            llm_response = await self._llm.complete(
                system_prompt=self._build_system_prompt(context),
                messages=[{"role": "user", "content": user_msg_content}],
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
            )

            # --- Update strategy memory ---
            user_message = self._make_message(experiment.id, turn_number, MessageRole.USER, user_msg_content)
            assistant_message = self._make_message(experiment.id, turn_number, MessageRole.ASSISTANT, llm_response.content, llm_response)
            strategy.update_memory(user_message)
            strategy.update_memory(assistant_message)

            cumulative_tokens += llm_response.total_tokens
            cumulative_cost += llm_response.cost_usd
            await self._logger.log_turn(experiment.id, user_message, assistant_message, llm_response)

            # --- Recall testing at intervals ---
            if self._recall_engine.should_test(turn_number):
                results = await self._recall_engine.run_recall_tests(
                    facts, turn_number, strategy, experiment.id
                )
                all_recall_results.extend(results)
                snapshot = self._metrics_engine.compute_snapshot(
                    experiment_id=experiment.id,
                    turn_number=turn_number,
                    results_at_turn=results,
                    all_results_so_far=all_recall_results,
                    facts=facts,
                    cumulative_tokens=cumulative_tokens,
                    cumulative_cost=cumulative_cost,
                    cumulative_latency_ms=0.0,
                    result_count=len(all_recall_results),
                )
                all_snapshots.append(snapshot)
                await self._logger.log_metrics_snapshot(snapshot)
                logger.info(
                    "Turn %d | recall_accuracy=%.3f | tokens=%d | cost=$%.4f",
                    turn_number, snapshot.memory_recall_accuracy, cumulative_tokens, cumulative_cost,
                )

        logger.info("Pipeline complete for experiment %s", experiment.id)

    def _build_system_prompt(self, memory_context: str) -> str:
        base = "You are a helpful, friendly assistant in a natural conversation."
        if memory_context:
            return f"{base}\n\n{memory_context}"
        return base

    def _make_message(self, experiment_id: str, turn: int, role: MessageRole, content: str, llm_response=None) -> Message:
        import uuid
        return Message(
            id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            turn_number=turn,
            role=role,
            content=content,
            tokens=llm_response.total_tokens if llm_response else 0,
            latency_ms=llm_response.latency_ms if llm_response else None,
            cost_usd=llm_response.cost_usd if llm_response else None,
        )

    async def _load_conversation_turns(self, experiment_id: str) -> list[tuple[str, str]]:
        """Load pre-generated conversation turns from DB."""
        # TODO: implement — load from message repository
        raise NotImplementedError
