"""Strategies API endpoints."""
from __future__ import annotations
from fastapi import APIRouter

from app.strategies.registry import registry
from app.schemas.strategy import StrategyListResponse, StrategyResponse

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("", response_model=StrategyListResponse)
async def list_strategies() -> StrategyListResponse:
    """List all registered memory strategies."""
    strategies = registry.list_strategies()
    return StrategyListResponse(
        strategies=[
            StrategyResponse(
                name=s["name"],
                description=s["description"],
                class_name=s["class"],
            )
            for s in strategies
        ]
    )
