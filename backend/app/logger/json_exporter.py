"""
JSON Exporter.
Reads experiment JSONL files and exports full experiment data as a single
portable JSON bundle — for sharing experiments, papers, and reproducing results.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from app.core.config.settings import settings


class JSONExporter:
    """
    Bundles all experiment files into a single shareable JSON document.
    Format is stable — external tools can import it.
    """

    def __init__(self, results_dir: str | None = None) -> None:
        self._results_dir = Path(results_dir or settings.RESULTS_DIR)

    def export(self, experiment_id: str) -> dict[str, Any]:
        """
        Export one experiment as a full JSON bundle.

        Returns a dict with keys: config, facts, conversation, recall_results, metrics.
        """
        exp_dir = self._results_dir / experiment_id
        if not exp_dir.exists():
            raise FileNotFoundError(f"Experiment directory not found: {exp_dir}")

        return {
            "experiment_id": experiment_id,
            "config": self._read_json(exp_dir / "config.json"),
            "facts": self._read_json(exp_dir / "facts.json"),
            "conversation": self._read_jsonl(exp_dir / "conversation.jsonl"),
            "recall_results": self._read_jsonl(exp_dir / "recall_results.jsonl"),
            "metrics": self._read_jsonl(exp_dir / "metrics.jsonl"),
        }

    def save_bundle(self, experiment_id: str, output_path: str | None = None) -> Path:
        """Save the JSON bundle to a file."""
        bundle = self.export(experiment_id)
        path = Path(output_path or (self._results_dir / f"{experiment_id}_export.json"))
        path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def _read_json(path: Path) -> Any:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        return [json.loads(line) for line in lines if line.strip()]
