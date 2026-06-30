"""
Fact Injection Engine.
Places ground-truth facts into generated conversations at specified positions.
Produces the Fact entities that become the benchmark's ground truth.
"""
from __future__ import annotations
import uuid
import random

from app.core.config.experiment_config import FactConfig
from app.domain.entities.fact import Fact, FactType
from app.generators.conversation_generator import GeneratedConversation


# Built-in fact templates — the framework ships with common patterns
# New fact types can be added here without changing any other module
FACT_TEMPLATES: dict[str, list[dict]] = {
    "personal": [
        {"text": "My name is {value}.", "question": "What is my name?", "value_type": "name"},
        {"text": "I am {value} years old.", "question": "How old am I?", "value_type": "age"},
        {"text": "My favorite color is {value}.", "question": "What is my favorite color?", "value_type": "color"},
        {"text": "I own a {value}.", "question": "What car do I own?", "value_type": "car"},
        {"text": "I study {value}.", "question": "What do I study?", "value_type": "subject"},
    ],
    "technical": [
        {"text": "The API key is {value}.", "question": "What is the API key?", "value_type": "api_key"},
        {"text": "The server runs on port {value}.", "question": "What port does the server run on?", "value_type": "port"},
        {"text": "The database is named {value}.", "question": "What is the database name?", "value_type": "db_name"},
    ],
    "temporal": [
        {"text": "My birthday is {value}.", "question": "When is my birthday?", "value_type": "date"},
        {"text": "The meeting is on {value}.", "question": "When is the meeting?", "value_type": "date"},
        {"text": "I started working here on {value}.", "question": "When did I start working here?", "value_type": "date"},
    ],
    "spatial": [
        {"text": "I live in {value}.", "question": "Where do I live?", "value_type": "city"},
        {"text": "My office is at {value}.", "question": "Where is my office?", "value_type": "address"},
    ],
}


class FactInjector:
    """
    Generates Fact entities and injects them into a GeneratedConversation.

    The injector modifies the conversation turns at injection positions,
    wrapping facts in natural-sounding dialogue that a real user might say.
    """

    def __init__(self) -> None:
        self._rng: random.Random | None = None

    def generate_facts(self, config: FactConfig) -> list[Fact]:
        """
        Generate a set of Fact entities from the config specification.

        Args:
            config: Fact configuration (count, types, difficulty range, seed).

        Returns:
            List of Facts with unique IDs, questions, and expected answers.
        """
        # TODO: implement
        raise NotImplementedError

    def inject_into_conversation(
        self,
        conversation: GeneratedConversation,
        facts: list[Fact],
    ) -> GeneratedConversation:
        """
        Inject facts into the conversation at the pre-marked positions.
        Modifies user turns to naturally contain the fact text.

        Args:
            conversation: The generated conversation with injection slots.
            facts: Facts to inject (len must match injection_positions).

        Returns:
            Modified conversation with facts embedded.
        """
        # TODO: implement
        raise NotImplementedError

    def _wrap_fact_naturally(self, fact_text: str, topic: str) -> str:
        """
        Wrap a bare fact ("My name is Nilina.") in natural conversation context.
        Example: "By the way, my name is Nilina. Anyway, back to what we were discussing..."
        """
        # TODO: implement — use templates or LLM to make injection sound natural
        raise NotImplementedError

    def _generate_fact_value(self, value_type: str, rng: random.Random) -> str:
        """Generate a realistic value for a given value type."""
        # TODO: implement — value pools for names, dates, cities, etc.
        raise NotImplementedError
