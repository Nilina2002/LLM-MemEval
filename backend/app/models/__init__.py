"""
Import all ORM models here so SQLAlchemy's metadata knows about every table.
This file is imported by database/session.py before create_all().
"""
from app.models.experiment import ExperimentModel
from app.models.fact import FactModel
from app.models.message import MessageModel
from app.models.recall_result import RecallResultModel
from app.models.metrics_snapshot import MetricsSnapshotModel

__all__ = [
    "ExperimentModel",
    "FactModel",
    "MessageModel",
    "RecallResultModel",
    "MetricsSnapshotModel",
]
