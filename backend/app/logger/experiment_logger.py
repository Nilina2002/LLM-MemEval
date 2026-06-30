"""
Experiment Logger — full dual-write implementation.
Writes to both SQLite (queryable) and JSONL files (portable/reproducible).
"""
from __future__ import annotations
import json
import logging
from dataclasses import asdict
from pathlib import Path
from datetime import datetime

from app.domain.entities.message import Message
from app.domain.entities.recall_result import RecallResult
from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.domain.entities.fact import Fact
from app.domain.interfaces.llm_provider import LLMResponse
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


def _default_json(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "value"):   # Enum
        return obj.value
    return str(obj)


class ExperimentLogger:
    """
    Dual-write logger: SQLite rows AND append-only JSONL files.

    File layout per experiment:
      results/{experiment_id}/
        config.json          — experiment config (written once at start)
        facts.json           — all injected facts (written once)
        conversation.jsonl   — one line per turn
        recall_results.jsonl — one line per recall test
        metrics.jsonl        — one line per checkpoint snapshot
    """

    def __init__(self, results_dir: str | None = None) -> None:
        self._results_dir = Path(results_dir or settings.RESULTS_DIR)

    # ── Experiment-level ──────────────────────────────────────────────────────

    async def log_config(self, experiment_id: str, config: dict) -> None:
        path = self._exp_dir(experiment_id) / "config.json"
        path.write_text(json.dumps(config, indent=2, default=_default_json), encoding="utf-8")
        logger.debug("Logged config for experiment %s", experiment_id)

    async def log_facts(self, experiment_id: str, facts: list[Fact]) -> None:
        records = []
        for f in facts:
            records.append({
                "fact_id": f.fact_id,
                "text": f.text,
                "expected_answer": f.expected_answer,
                "recall_question": f.recall_question,
                "insertion_turn": f.insertion_turn,
                "fact_type": f.fact_type.value,
                "difficulty": f.difficulty,
                "importance": f.importance,
                "tags": f.tags,
                "alternative_answers": f.alternative_answers,
            })
        path = self._exp_dir(experiment_id) / "facts.json"
        path.write_text(json.dumps(records, indent=2, default=_default_json), encoding="utf-8")
        logger.debug("Logged %d facts for experiment %s", len(facts), experiment_id)

    # ── Turn-level ────────────────────────────────────────────────────────────

    async def log_turn(
        self,
        experiment_id: str,
        user_message: Message,
        assistant_message: Message,
        llm_response: LLMResponse,
    ) -> None:
        record = {
            "turn": user_message.turn_number,
            "user": user_message.content,
            "assistant": assistant_message.content,
            "tokens_prompt": llm_response.prompt_tokens,
            "tokens_completion": llm_response.completion_tokens,
            "tokens_total": llm_response.total_tokens,
            "cost_usd": llm_response.cost_usd,
            "latency_ms": llm_response.latency_ms,
            "model": llm_response.model,
            "contains_fact": user_message.contains_injected_fact,
            "fact_id": user_message.fact_id,
            "ts": datetime.utcnow().isoformat(),
        }
        self._append_jsonl(experiment_id, "conversation.jsonl", record)

    # ── Recall-level ──────────────────────────────────────────────────────────

    async def log_recall_result(self, result: RecallResult) -> None:
        record = {
            "id": result.id,
            "fact_id": result.fact_id,
            "test_turn": result.test_turn,
            "question": result.question,
            "expected": result.expected_answer,
            "model_answer": result.model_answer,
            "is_correct": result.is_correct,
            "score": result.similarity_score,
            "method": result.scoring_method,
            "prompt_tokens": result.prompt_tokens,
            "response_tokens": result.response_tokens,
            "latency_ms": result.latency_ms,
            "cost_usd": result.cost_usd,
            "retrieved_context_len": len(result.retrieved_context),
            "ts": result.timestamp.isoformat(),
        }
        self._append_jsonl(result.experiment_id, "recall_results.jsonl", record)

    # ── Metrics-level ─────────────────────────────────────────────────────────

    async def log_metrics_snapshot(self, snapshot: MetricsSnapshot) -> None:
        record = {
            "turn": snapshot.turn_number,
            "accuracy": snapshot.memory_recall_accuracy,
            "lt_recall": snapshot.long_term_recall_rate,
            "retention": snapshot.information_retention_rate,
            "forgetting_rate": snapshot.forgetting_rate,
            "survival_score": snapshot.information_survival_score,
            "precision": snapshot.retrieval_precision,
            "recall": snapshot.retrieval_recall,
            "tokens": snapshot.total_tokens,
            "cost_usd": snapshot.total_cost_usd,
            "latency_ms": snapshot.avg_latency_ms,
            "token_efficiency": snapshot.token_efficiency,
            "per_fact": snapshot.per_fact_scores,
            "ts": snapshot.timestamp.isoformat(),
        }
        self._append_jsonl(snapshot.experiment_id, "metrics.jsonl", record)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _exp_dir(self, experiment_id: str) -> Path:
        path = self._results_dir / experiment_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _append_jsonl(self, experiment_id: str, filename: str, record: dict) -> None:
        path = self._exp_dir(experiment_id) / filename
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=_default_json) + "\n")
