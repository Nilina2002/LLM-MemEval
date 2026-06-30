"""Pydantic schemas for strategy API responses."""
from __future__ import annotations
from pydantic import BaseModel


class StrategyResponse(BaseModel):
    name: str
    description: str
    class_name: str


class StrategyListResponse(BaseModel):
    strategies: list[StrategyResponse]
