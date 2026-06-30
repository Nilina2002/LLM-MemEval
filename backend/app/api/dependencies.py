"""
FastAPI dependency injection factories.
All collaborators are wired here — endpoints only declare what they need.
"""
from __future__ import annotations
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.repositories.experiment_repository import SQLExperimentRepository
from app.strategies.registry import registry
from app.services.experiment_service import ExperimentService
from app.experiments.orchestrator import ExperimentOrchestrator
from app.experiments.pipeline import ExperimentPipeline
from app.metrics.engine import MetricsEngine
from app.logger.experiment_logger import ExperimentLogger


async def get_db() -> AsyncSession:
    """Yield a database session for the request lifetime."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_experiment_service(
    db: AsyncSession = Depends(get_db),
) -> ExperimentService:
    """
    Construct the full dependency graph for experiment operations.
    All wiring happens here — endpoints stay clean.
    """
    experiment_repo = SQLExperimentRepository(db)
    metrics_engine = MetricsEngine()
    exp_logger = ExperimentLogger()

    # Pipeline requires additional repos and LLM provider
    # Full wiring happens when we implement the pipeline in Step 6
    pipeline = ExperimentPipeline(
        llm_provider=None,         # TODO: inject from settings
        recall_engine=None,        # TODO: inject
        metrics_engine=metrics_engine,
        experiment_logger=exp_logger,
        fact_repo=None,            # TODO: inject
        strategy_registry=registry,
    )

    orchestrator = ExperimentOrchestrator(
        experiment_repo=experiment_repo,
        pipeline=pipeline,
        strategy_registry=registry,
    )

    return ExperimentService(orchestrator=orchestrator)
