"""
Strategy Comparison figure builder.
Overlays decay curves from multiple experiments/strategies on one chart.
"""
from __future__ import annotations
from typing import Any


def build_strategy_comparison(
    experiments: list[dict],  # [{"name": str, "strategy": str, "snapshots": list}]
) -> dict[str, Any]:
    """
    Multi-line decay curve for comparing strategies head-to-head.
    This is the primary figure for published research comparisons.
    """
    traces = []
    for exp in experiments:
        snapshots = exp["snapshots"]
        turns = [s.turn_number for s in snapshots]
        accuracies = [s.memory_recall_accuracy for s in snapshots]
        traces.append({
            "type": "scatter",
            "mode": "lines+markers",
            "x": turns,
            "y": accuracies,
            "name": f"{exp['strategy']} ({exp['name']})",
            "line": {"width": 2},
        })

    return {
        "data": traces,
        "layout": {
            "title": "Memory Strategy Comparison — Recall Accuracy",
            "xaxis": {"title": "Conversation Turn"},
            "yaxis": {"title": "Recall Accuracy", "range": [0, 1.05]},
            "legend": {"x": 0.75, "y": 0.95},
            "template": "plotly_dark",
            "hovermode": "x unified",
        },
    }
