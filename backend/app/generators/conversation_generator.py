"""
Conversation Generator — full implementation.

Produces realistic multi-turn conversations from domain-specific templates.
Generation is deterministic: the same seed always produces the same conversation.

Design decisions:
- Template-based (no LLM required) so experiments run without API credits.
- Domain templates are pluggable — add a new domain by adding a template module.
- Injection slots are marked BEFORE generation so fact text is never paraphrased by templates.
- Topics cycle with natural variation via the seeded RNG.
"""
from __future__ import annotations
import random
import importlib
from dataclasses import dataclass, field
from typing import Any

from app.core.config.experiment_config import ConversationConfig
from app.core.constants import INJECT_SLOT_MARKER, MAX_CONVERSATION_TURNS


@dataclass
class GeneratedTurn:
    """One conversation turn with all metadata needed by the pipeline."""
    turn_number: int
    user_message: str
    assistant_message: str    # Template placeholder; LLM overwrites during run
    topic: str
    is_injection_slot: bool = False
    injection_slot_id: int | None = None
    contains_injected_fact: bool = False


@dataclass
class GeneratedConversation:
    """Complete generated conversation ready for fact injection."""
    config: ConversationConfig
    turns: list[GeneratedTurn] = field(default_factory=list)
    injection_positions: list[int] = field(default_factory=list)

    def get_turn(self, turn_number: int) -> GeneratedTurn | None:
        idx = turn_number - 1
        return self.turns[idx] if 0 <= idx < len(self.turns) else None

    def get_injection_turns(self) -> list[GeneratedTurn]:
        return [t for t in self.turns if t.is_injection_slot]


# Domain → template module mapping
_DOMAIN_MODULES = {
    "casual":       "app.generators.templates.casual",
    "programming":  "app.generators.templates.programming",
    "education":    "app.generators.templates.education",
    "travel":       "app.generators.templates.travel",
    "shopping":     "app.generators.templates.shopping",
}


class ConversationGenerator:
    """
    Generates deterministic multi-turn conversations for benchmark experiments.

    The generator creates user messages only. During the experiment run, the LLM
    generates real assistant responses — the template assistant messages are placeholders
    that will never be sent to the model.
    """

    # Min/max turns on the same topic before shifting
    _MIN_TOPIC_TURNS = 2
    _MAX_TOPIC_TURNS = 6

    def generate(
        self,
        config: ConversationConfig,
        injection_positions: list[int],
    ) -> GeneratedConversation:
        """
        Generate a complete conversation with marked injection slots.

        Args:
            config: Conversation configuration (domain, turns, seed).
            injection_positions: Turn numbers where facts will be injected.

        Returns:
            GeneratedConversation with every turn populated.
        """
        if config.total_turns > MAX_CONVERSATION_TURNS:
            raise ValueError(
                f"total_turns={config.total_turns} exceeds maximum {MAX_CONVERSATION_TURNS}."
            )

        rng = random.Random(config.seed)
        injection_set = set(injection_positions)

        # Load templates for the specified domain
        templates = self._load_domain_templates(config.domain)

        # Generate the topic sequence
        topic_sequence = self._generate_topic_sequence(
            templates["get_topics"](), config.total_turns, rng
        )

        turns: list[GeneratedTurn] = []
        for i in range(config.total_turns):
            turn_number = i + 1
            topic = topic_sequence[i]
            is_injection = turn_number in injection_set

            if is_injection:
                slot_id = sorted(injection_positions).index(turn_number)
                user_msg = INJECT_SLOT_MARKER.format(n=slot_id)
                assistant_msg = ""   # Placeholder — LLM generates during run
            else:
                user_msg = templates["get_user_message"](topic, rng)
                assistant_msg = templates["get_assistant_message"](topic, rng)

            turns.append(GeneratedTurn(
                turn_number=turn_number,
                user_message=user_msg,
                assistant_message=assistant_msg,
                topic=topic,
                is_injection_slot=is_injection,
                injection_slot_id=sorted(injection_positions).index(turn_number) if is_injection else None,
            ))

        return GeneratedConversation(
            config=config,
            turns=turns,
            injection_positions=injection_positions,
        )

    def calculate_injection_positions(
        self,
        total_turns: int,
        fact_count: int,
        strategy: str,
        seed: int,
    ) -> list[int]:
        """
        Determine which turns will receive fact injections.

        Args:
            total_turns: Total conversation length.
            fact_count: Number of facts to inject.
            strategy: Placement strategy ('uniform', 'early', 'late', 'random').
            seed: RNG seed for reproducibility.

        Returns:
            Sorted list of turn numbers for injection.
        """
        rng = random.Random(seed)
        # Protect first 5 and last 5 turns from injection
        safe_start = min(5, total_turns // 10)
        safe_end = max(safe_start + fact_count, total_turns - safe_start)

        available = list(range(safe_start, safe_end + 1))
        if len(available) < fact_count:
            # Not enough safe positions — widen the range
            available = list(range(1, total_turns + 1))

        if strategy == "uniform":
            if fact_count == 1:
                return [(safe_start + safe_end) // 2]
            step = max(1, (safe_end - safe_start) // (fact_count - 1))
            return sorted([safe_start + i * step for i in range(fact_count)])

        elif strategy == "early":
            early_end = max(safe_start + fact_count, total_turns // 4)
            early_pool = [t for t in available if t <= early_end]
            if len(early_pool) < fact_count:
                early_pool = available
            return sorted(rng.sample(early_pool, min(fact_count, len(early_pool))))

        elif strategy == "late":
            late_start = int(total_turns * 0.65)
            late_pool = [t for t in available if t >= late_start]
            if len(late_pool) < fact_count:
                late_pool = available
            return sorted(rng.sample(late_pool, min(fact_count, len(late_pool))))

        else:  # "random"
            return sorted(rng.sample(available, min(fact_count, len(available))))

    def _generate_topic_sequence(
        self, topics: list[str], total_turns: int, rng: random.Random
    ) -> list[str]:
        """
        Generate a natural topic sequence where each topic runs for 2–6 turns
        before shifting, mimicking real conversational flow.
        """
        sequence: list[str] = []
        remaining = total_turns
        current_topic = rng.choice(topics)

        while remaining > 0:
            # Stay on topic for 2–6 turns
            run_length = min(
                rng.randint(self._MIN_TOPIC_TURNS, self._MAX_TOPIC_TURNS),
                remaining,
            )
            sequence.extend([current_topic] * run_length)
            remaining -= run_length

            # Shift to a different topic
            other_topics = [t for t in topics if t != current_topic]
            current_topic = rng.choice(other_topics) if other_topics else current_topic

        return sequence[:total_turns]

    def _load_domain_templates(self, domain: str) -> dict[str, Any]:
        """
        Dynamically load the template module for a domain.
        Falls back to casual for unknown domains.
        """
        if domain == "mixed":
            # Mixed: cycle through all domains
            return self._build_mixed_templates()

        module_path = _DOMAIN_MODULES.get(domain, _DOMAIN_MODULES["casual"])
        module = importlib.import_module(module_path)
        return {
            "get_topics": module.get_topics,
            "get_user_message": module.get_user_message,
            "get_assistant_message": module.get_assistant_message,
        }

    def _build_mixed_templates(self) -> dict[str, Any]:
        """For 'mixed' domain, combine all template modules."""
        all_modules = [
            importlib.import_module(path) for path in _DOMAIN_MODULES.values()
        ]
        all_topics = []
        for m in all_modules:
            all_topics.extend(m.get_topics())

        def get_topics():
            return all_topics

        def get_user_message(topic: str, rng: random.Random) -> str:
            for m in all_modules:
                try:
                    return m.get_user_message(topic, rng)
                except Exception:
                    continue
            return "What do you think about that?"

        def get_assistant_message(topic: str, rng: random.Random) -> str:
            for m in all_modules:
                try:
                    return m.get_assistant_message(topic, rng)
                except Exception:
                    continue
            return "Interesting point. Tell me more."

        return {
            "get_topics": get_topics,
            "get_user_message": get_user_message,
            "get_assistant_message": get_assistant_message,
        }
