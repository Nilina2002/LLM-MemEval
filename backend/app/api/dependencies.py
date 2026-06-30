"""
FastAPI dependency injection — full wiring.
All module wiring happens here. Endpoint functions declare only what they need.
"""
from __future__ import annotations
from functools import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal, get_db_session
from app.repositories.experiment_repository import SQLExperimentRepository
from app.repositories.fact_repository import SQLFactRepositoryWithExperiment
from app.repositories.message_repository import SQLMessageRepository
from app.repositories.recall_repository import SQLRecallRepository
from app.repositories.metrics_repository import SQLMetricsRepository
from app.strategies.registry import registry
from app.services.experiment_service import ExperimentService
from app.experiments.orchestrator import ExperimentOrchestrator
from app.experiments.pipeline import ExperimentPipeline
from app.metrics.engine import MetricsEngine
from app.logger.experiment_logger import ExperimentLogger
from app.visualization.engine import VisualizationEngine
from app.infrastructure.llm.factory import create_llm_provider
from app.core.config.experiment_config import LLMConfig
from app.core.config.settings import settings


async def get_db() -> AsyncSession:
    """Yield a database session scoped to the HTTP request."""
    async with get_db_session() as session:
        yield session


def get_default_llm_provider():
    """Return a default LLM provider for use inside the pipeline."""
    default_config = LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=512,
    )
    return create_llm_provider(default_config)


async def get_experiment_service():
    """
    Build the full dependency graph for experiment operations.
    Uses get_db_session so the session commits on success and rolls back on error.
    """
    async with get_db_session() as session:
        experiment_repo = SQLExperimentRepository(session)
        metrics_engine = MetricsEngine()
        exp_logger = ExperimentLogger()
        viz_engine = VisualizationEngine()

        try:
            llm_provider = get_default_llm_provider()
        except Exception:
            llm_provider = None

        pipeline = ExperimentPipeline(
            llm_provider=llm_provider,
            strategy_registry=registry,
            exp_logger=exp_logger,
            metrics_engine=metrics_engine,
            viz_engine=viz_engine,
            db_session=session,
        )

        orchestrator = ExperimentOrchestrator(
            experiment_repo=experiment_repo,
            pipeline=pipeline,
            strategy_registry=registry,
        )

        yield ExperimentService(orchestrator=orchestrator)


class DependencyContainer:
    """
    Singleton container for expensive-to-create shared resources.
    Avoids reconstructing embedding models, DB connections, etc. on every request.
    """
    _metrics_engine: MetricsEngine | None = None
    _exp_logger: ExperimentLogger | None = None
    _viz_engine: VisualizationEngine | None = None

    @classmethod
    def metrics_engine(cls) -> MetricsEngine:
        if cls._metrics_engine is None:
            cls._metrics_engine = MetricsEngine()
        return cls._metrics_engine

    @classmethod
    def exp_logger(cls) -> ExperimentLogger:
        if cls._exp_logger is None:
            cls._exp_logger = ExperimentLogger()
        return cls._exp_logger

    @classmethod
    def viz_engine(cls) -> VisualizationEngine:
        if cls._viz_engine is None:
            cls._viz_engine = VisualizationEngine()
        return cls._viz_engine
