"""
Visualization Engine.
Generates Plotly figures from experiment data.
Figures are returned as JSON dicts — the frontend renders them via react-plotly.js.
"""
from __future__ import annotations
import logging
from typing import Any

from app.domain.entities.metrics_snapshot import MetricsSnapshot
from app.domain.entities.fact import Fact
from app.domain.entities.recall_result import RecallResult

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Produces all research visualizations as Plotly JSON specs.
    No matplotlib — Plotly JSON is renderable on both server and client.
    """

    def memory_decay_curve(
        self,
        snapshots: list[MetricsSnapshot],
        strategy_name: str,
        experiment_name: str,
    ) -> dict[str, Any]:
        """
        Primary research visualization: recall accuracy vs. conversation turn.
        Shows HOW FAST and HOW MUCH the model forgets.
        """
        from app.visualization.figures.decay_curve import build_decay_curve
        return build_decay_curve(snapshots, strategy_name, experiment_name)

    def strategy_comparison(
        self,
        experiments: list[dict],  # [{name, strategy, snapshots}]
    ) -> dict[str, Any]:
        """
        Overlay multiple strategies' decay curves on one chart.
        The key comparison figure for published research.
        """
        from app.visualization.figures.strategy_comparison import build_strategy_comparison
        return build_strategy_comparison(experiments)

    def fact_survival_timeline(
        self,
        facts: list[Fact],
        recall_results: list[RecallResult],
    ) -> dict[str, Any]:
        """
        Heatmap: fact × recall_turn → correct/incorrect.
        Shows which facts survive and which are forgotten first.
        """
        from app.visualization.figures.fact_timeline import build_fact_timeline
        return build_fact_timeline(facts, recall_results)

    def token_usage_chart(self, snapshots: list[MetricsSnapshot]) -> dict[str, Any]:
        """Token consumption and API cost over time."""
        # TODO: implement
        raise NotImplementedError

    def forgetting_rate_histogram(self, snapshots: list[MetricsSnapshot]) -> dict[str, Any]:
        """Distribution of forgetting rates across fact types and intervals."""
        # TODO: implement
        raise NotImplementedError

    def generate_all(
        self,
        snapshots: list[MetricsSnapshot],
        facts: list[Fact],
        recall_results: list[RecallResult],
        strategy_name: str,
        experiment_name: str,
    ) -> dict[str, dict[str, Any]]:
        """Generate all standard figures for one experiment."""
        return {
            "decay_curve": self.memory_decay_curve(snapshots, strategy_name, experiment_name),
            "fact_survival": self.fact_survival_timeline(facts, recall_results),
        }
