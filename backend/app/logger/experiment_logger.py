"""
Experiment Logger.
Writes every event to both the database and JSON files for complete reproducibility.
"""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path

from app.domain.entities.message import Message
from app.domain.entities.recall_result import RecallResult
from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.domain.interfaces.llm_provider import LLMResponse
from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class ExperimentLogger:
    """
    Dual-write logger: structured DB rows + append-only JSONL files.
    JSONL files make experiments shareable and reproducible outside the database.
    """

    def __init__(self, results_dir: str | None = None) -> None:
        self._results_dir = Path(results_dir or settings.RESULTS_DIR)

    def _experiment_dir(self, experiment_id: str) -> Path:
        path = self._results_dir / experiment_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _append_jsonl(self, path: Path, record: dict) -> None:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    async def log_config(self, experiment_id: str, config: dict) -> None:
        """Write experiment configuration as JSON (once at start)."""
        config_path = self._experiment_dir(experiment_id) / "config.json"
        config_path.write_text(json.dumps(config, indent=2, default=str))

    async def log_facts(self, experiment_id: str, facts: list) -> None:
        """Write all injected facts as JSON (once at start)."""
        facts_path = self._experiment_dir(experiment_id) / "facts.json"
        # TODO: serialize facts to dict
        raise NotImplementedError

    async def log_turn(
        self,
        experiment_id: str,
        user_message: Message,
        assistant_message: Message,
        llm_response: LLMResponse,
    ) -> None:
        """Append one conversation turn to conversation.jsonl."""
        record = {
            "turn": user_message.turn_number,
            "user": user_message.content,
            "assistant": assistant_message.content,
            "tokens": llm_response.total_tokens,
            "cost_usd": llm_response.cost_usd,
            "latency_ms": llm_response.latency_ms,
        }
        path = self._experiment_dir(experiment_id) / "conversation.jsonl"
        self._append_jsonl(path, record)

    async def log_recall_result(self, result: RecallResult) -> None:
        """Append one recall test result to recall_results.jsonl."""
        # TODO: implement serialization
        raise NotImplementedError

    async def log_metrics_snapshot(self, snapshot: MetricsSnapshot) -> None:
        """Append one metrics snapshot to metrics.jsonl."""
        # TODO: implement serialization
        raise NotImplementedError
