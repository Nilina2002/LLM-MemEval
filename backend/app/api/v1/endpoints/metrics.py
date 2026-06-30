"""Metrics and graphs API endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.metrics import (
    ExperimentMetricsResponse,
    MetricsSnapshotResponse,
    CompareExperimentsRequest,
    CompareExperimentsResponse,
)
from app.api.dependencies import get_db, DependencyContainer
from app.repositories.metrics_repository import SQLMetricsRepository
from app.repositories.experiment_repository import SQLExperimentRepository
from app.repositories.recall_repository import SQLRecallRepository
from app.repositories.fact_repository import SQLFactRepository
from app.metrics.engine import MetricsEngine
from app.visualization.engine import VisualizationEngine
from app.core.exceptions import ExperimentNotFoundError

router = APIRouter(tags=["metrics"])


@router.get("/experiments/{experiment_id}/metrics", response_model=ExperimentMetricsResponse)
async def get_metrics(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> ExperimentMetricsResponse:
    """Return all metrics snapshots for an experiment."""
    exp_repo = SQLExperimentRepository(db)
    metrics_repo = SQLMetricsRepository(db)
    metrics_engine = DependencyContainer.metrics_engine()

    experiment = await exp_repo.get_by_id(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found.")

    snapshots = await metrics_repo.get_by_experiment(experiment_id)
    summary = metrics_engine.compute_experiment_summary(snapshots)

    return ExperimentMetricsResponse(
        experiment_id=experiment_id,
        strategy_name=experiment.strategy_name,
        snapshots=[
            MetricsSnapshotResponse(
                turn_number=s.turn_number,
                memory_recall_accuracy=s.memory_recall_accuracy,
                long_term_recall_rate=s.long_term_recall_rate,
                forgetting_rate=s.forgetting_rate,
                information_survival_score=s.information_survival_score,
                total_tokens=s.total_tokens,
                total_cost_usd=s.total_cost_usd,
                avg_latency_ms=s.avg_latency_ms,
                token_efficiency=s.token_efficiency,
                timestamp=s.timestamp,
            )
            for s in snapshots
        ],
        summary=summary,
    )


@router.get("/experiments/{experiment_id}/graphs")
async def get_graphs(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return Plotly figure JSON for all standard charts."""
    exp_repo = SQLExperimentRepository(db)
    metrics_repo = SQLMetricsRepository(db)
    recall_repo = SQLRecallRepository(db)
    fact_repo = SQLFactRepository(db)
    viz_engine = DependencyContainer.viz_engine()

    experiment = await exp_repo.get_by_id(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} not found.")

    snapshots = await metrics_repo.get_by_experiment(experiment_id)
    recall_results = await recall_repo.get_by_experiment(experiment_id)
    facts = await fact_repo.get_by_experiment(experiment_id)

    if not snapshots:
        return {"message": "No metrics data yet — run the experiment first.", "figures": {}}

    figures = viz_engine.generate_all(
        snapshots=snapshots,
        facts=facts,
        recall_results=recall_results,
        strategy_name=experiment.strategy_name,
        experiment_name=experiment.name,
    )
    return {"figures": figures}


@router.post("/compare", response_model=CompareExperimentsResponse)
async def compare_experiments(
    request: CompareExperimentsRequest,
    db: AsyncSession = Depends(get_db),
) -> CompareExperimentsResponse:
    """Compare metrics across multiple experiments with an overlay chart."""
    exp_repo = SQLExperimentRepository(db)
    metrics_repo = SQLMetricsRepository(db)
    viz_engine = DependencyContainer.viz_engine()

    experiment_data = []
    for eid in request.experiment_ids:
        experiment = await exp_repo.get_by_id(eid)
        if experiment is None:
            raise HTTPException(status_code=404, detail=f"Experiment {eid} not found.")
        snapshots = await metrics_repo.get_by_experiment(eid)
        experiment_data.append({
            "id": eid,
            "name": experiment.name,
            "strategy": experiment.strategy_name,
            "snapshots": snapshots,
        })

    comparison_chart = viz_engine.strategy_comparison(experiment_data)

    return CompareExperimentsResponse(
        experiments=[{"id": d["id"], "name": d["name"], "strategy": d["strategy"]} for d in experiment_data],
        comparison_chart=comparison_chart,
    )
