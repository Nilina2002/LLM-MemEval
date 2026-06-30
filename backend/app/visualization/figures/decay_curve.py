"""
Memory Decay Curve figure builder.
Recall accuracy vs. conversation turn number.
"""
from __future__ import annotations
from typing import Any

from app.domain.entities.metrics_snapshot import MetricsSnapshot


def build_decay_curve(
    snapshots: list[MetricsSnapshot],
    strategy_name: str,
    experiment_name: str,
) -> dict[str, Any]:
    """
    Returns a Plotly figure dict showing recall accuracy over conversation turns.

    Args:
        snapshots: Ordered list of MetricsSnapshots (one per recall interval).
        strategy_name: Used in the legend label.
        experiment_name: Used in the chart title.
    """
    turns = [s.turn_number for s in snapshots]
    accuracies = [s.memory_recall_accuracy for s in snapshots]
    survival_scores = [s.information_survival_score for s in snapshots]

    figure = {
        "data": [
            {
                "type": "scatter",
                "mode": "lines+markers",
                "x": turns,
                "y": accuracies,
                "name": f"{strategy_name} — Recall Accuracy",
                "line": {"width": 2},
                "marker": {"size": 6},
            },
            {
                "type": "scatter",
                "mode": "lines",
                "x": turns,
                "y": survival_scores,
                "name": f"{strategy_name} — Survival Score",
                "line": {"width": 1, "dash": "dash"},
            },
        ],
        "layout": {
            "title": f"Memory Decay Curve — {experiment_name}",
            "xaxis": {"title": "Conversation Turn"},
            "yaxis": {"title": "Score", "range": [0, 1.05]},
            "legend": {"x": 0.75, "y": 0.95},
            "template": "plotly_dark",
            "hovermode": "x unified",
        },
    }
    return figure
