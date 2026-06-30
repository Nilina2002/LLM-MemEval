"""
Fact Survival Timeline (heatmap).
Shows per-fact recall correctness at each recall checkpoint.
"""
from __future__ import annotations
from typing import Any

from app.domain.entities.fact import Fact
from app.domain.entities.recall_result import RecallResult


def build_fact_timeline(
    facts: list[Fact],
    recall_results: list[RecallResult],
) -> dict[str, Any]:
    """
    Returns a Plotly heatmap: rows=facts, columns=recall turns, cells=correct/incorrect.
    """
    fact_map = {f.fact_id: f for f in facts}
    turns = sorted(set(r.test_turn for r in recall_results))
    fact_ids = [f.fact_id for f in facts]
    fact_labels = [f.recall_question[:40] for f in facts]

    # Build correctness matrix: facts × turns
    result_lookup = {(r.fact_id, r.test_turn): r.similarity_score for r in recall_results}
    z_matrix = [
        [result_lookup.get((fid, t), None) for t in turns]
        for fid in fact_ids
    ]

    figure = {
        "data": [
            {
                "type": "heatmap",
                "z": z_matrix,
                "x": [f"Turn {t}" for t in turns],
                "y": fact_labels,
                "colorscale": "RdYlGn",
                "zmin": 0.0,
                "zmax": 1.0,
                "colorbar": {"title": "Recall Score"},
            }
        ],
        "layout": {
            "title": "Fact Survival Timeline",
            "xaxis": {"title": "Recall Checkpoint"},
            "yaxis": {"title": "Injected Fact"},
            "template": "plotly_dark",
        },
    }
    return figure
