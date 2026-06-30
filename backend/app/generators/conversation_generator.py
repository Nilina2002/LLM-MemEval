"""
Conversation Generator.
Produces realistic multi-turn conversations with injection slot markers.
Generation is deterministic given a fixed seed.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Literal

from app.core.config.experiment_config import ConversationConfig
from app.core.constants import INJECT_SLOT_MARKER


ConversationDomain = Literal["casual", "programming", "education", "travel", "shopping", "mixed"]


@dataclass
class ConversationOutline:
    """
    Pre-generated conversation blueprint.
    Contains topic sequence and injection slot positions before turns are filled.
    """
    domain: ConversationDomain
    total_turns: int
    topic_sequence: list[str]
    injection_positions: list[int]    # Turn indices reserved for fact injection
    seed: int


@dataclass
class GeneratedTurn:
    """A single generated conversation turn before fact injection."""
    turn_number: int
    user_message: str
    assistant_message: str
    topic: str
    is_injection_slot: bool = False
    injection_slot_id: int | None = None


@dataclass
class GeneratedConversation:
    """Complete generated conversation ready for fact injection."""
    config: ConversationConfig
    turns: list[GeneratedTurn] = field(default_factory=list)
    injection_positions: list[int] = field(default_factory=list)


class ConversationGenerator:
    """
    Generates realistic multi-turn conversations.

    Key design decisions:
    - Uses a seeded RNG for reproducibility.
    - Marks injection slots BEFORE generation so injected facts are never paraphrased.
    - Domain templates keep conversations coherent across hundreds of turns.
    """

    def __init__(self, llm_provider=None) -> None:
        self._llm = llm_provider    # Optional: use LLM to generate turns (higher quality)

    def generate(self, config: ConversationConfig, injection_positions: list[int]) -> GeneratedConversation:
        """
        Generate a complete conversation with injection slot markers.

        Args:
            config: Conversation configuration (domain, turns, seed).
            injection_positions: Turn indices where facts will be injected.

        Returns:
            GeneratedConversation with all turns populated.
        """
        # TODO: implement
        raise NotImplementedError

    def _build_outline(
        self, config: ConversationConfig, injection_positions: list[int]
    ) -> ConversationOutline:
        """Plan the topic sequence using the seeded RNG."""
        # TODO: implement
        raise NotImplementedError

    def _generate_turn(
        self,
        turn_number: int,
        topic: str,
        domain: ConversationDomain,
        rng: random.Random,
    ) -> GeneratedTurn:
        """Generate one conversation turn from a template."""
        # TODO: implement — use domain-specific templates or LLM
        raise NotImplementedError

    def _calculate_injection_positions(
        self, total_turns: int, fact_count: int, strategy: str, rng: random.Random
    ) -> list[int]:
        """
        Determine at which turns to inject facts.
        Strategies: 'uniform', 'early', 'late', 'random'.
        """
        # TODO: implement
        raise NotImplementedError
