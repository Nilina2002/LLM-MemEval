"""
Domain entity: Message.
A single turn in a conversation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """
    One turn in a conversation between user and assistant.
    Tracks token usage and whether this turn contains an injected fact.
    """
    id: str
    experiment_id: str
    turn_number: int
    role: MessageRole
    content: str
    tokens: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    contains_injected_fact: bool = False
    fact_id: str | None = None      # Set if this message carries an injected fact
    latency_ms: float | None = None # Time taken to generate this message
    cost_usd: float | None = None
