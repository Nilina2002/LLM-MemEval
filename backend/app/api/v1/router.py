"""
API v1 router — assembles all endpoint routers into /api/v1.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import experiments, strategies, metrics

router = APIRouter(prefix="/api/v1")

router.include_router(experiments.router)
router.include_router(strategies.router)
router.include_router(metrics.router)
