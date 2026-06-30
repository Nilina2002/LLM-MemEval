"""
Domain entity: Fact.
Represents a ground-truth fact injected into a conversation.
This is the fundamental unit of the benchmark.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class FactType(str, Enum):
    PERSONAL = "personal"        # name, age, preferences
    TECHNICAL = "technical"      # code, commands, configurations
    SPATIAL = "spatial"          # locations, directions
    TEMPORAL = "temporal"        # dates, schedules
    NUMERICAL = "numerical"      # numbers, quantities
    RELATIONAL = "relational"    # relationships between entities


@dataclass
class Fact:
    """
    A single ground-truth fact injected into the conversation.

    Every Fact is the atomic unit of the benchmark:
    it defines what was told to the model, when, and how to verify recall.
    """
    fact_id: str
    text: str                       # Full sentence as injected: "My name is Nilina."
    expected_answer: str            # Minimal correct answer: "Nilina"
    recall_question: str            # "What is my name?"
    insertion_turn: int             # Conversation turn where fact was injected
    fact_type: FactType
    difficulty: float               # 0.0 (easy) → 1.0 (hard)
    importance: float               # Weight in aggregate metrics
    tags: list[str] = field(default_factory=list)
    alternative_answers: list[str] = field(default_factory=list)  # acceptable variants

    def is_acceptable_answer(self, answer: str) -> bool:
        """Check if answer matches expected or any accepted alternative."""
        normalized = answer.strip().lower()
        if normalized == self.expected_answer.strip().lower():
            return True
        return any(normalized == alt.strip().lower() for alt in self.alternative_answers)
