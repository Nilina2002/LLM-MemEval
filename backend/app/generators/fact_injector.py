"""
Fact Injection Engine — full implementation.

Generates Fact entities from templates and injects them into conversations.
All generation is deterministic given a fixed seed.
"""
from __future__ import annotations
import random
import uuid
import logging
from dataclasses import asdict

from app.core.config.experiment_config import FactConfig
from app.domain.entities.fact import Fact, FactType
from app.generators.conversation_generator import GeneratedConversation, GeneratedTurn

logger = logging.getLogger(__name__)


# ── Fact template library ───────────────────────────────────────────────────
# Add new fact types here — no other file needs changing.

FACT_TEMPLATES: dict[str, list[dict]] = {
    "personal": [
        {"text": "My name is {value}.",                    "question": "What is my name?",             "value_type": "name"},
        {"text": "I am {value} years old.",                "question": "How old am I?",                "value_type": "age"},
        {"text": "My favorite color is {value}.",          "question": "What is my favorite color?",   "value_type": "color"},
        {"text": "I own a {value}.",                       "question": "What car do I own?",           "value_type": "car"},
        {"text": "I study {value}.",                       "question": "What do I study?",             "value_type": "subject"},
        {"text": "My favorite food is {value}.",           "question": "What is my favorite food?",    "value_type": "food"},
        {"text": "I work as a {value}.",                   "question": "What do I work as?",           "value_type": "job"},
        {"text": "My lucky number is {value}.",            "question": "What is my lucky number?",     "value_type": "number"},
        {"text": "My native language is {value}.",         "question": "What is my native language?",  "value_type": "language"},
        {"text": "My pet is called {value}.",              "question": "What is my pet's name?",       "value_type": "pet_name"},
    ],
    "technical": [
        {"text": "The server runs on port {value}.",       "question": "What port does the server run on?",   "value_type": "port"},
        {"text": "The database is named {value}.",         "question": "What is the database name?",          "value_type": "db_name"},
        {"text": "The project uses {value} as its framework.", "question": "What framework does the project use?", "value_type": "framework"},
        {"text": "The API base URL is {value}.",           "question": "What is the API base URL?",           "value_type": "url"},
        {"text": "The codebase is written in {value}.",    "question": "What language is the codebase in?",   "value_type": "language"},
        {"text": "The team uses {value} for version control.", "question": "What version control system does the team use?", "value_type": "vcs"},
        {"text": "The staging environment is at {value}.", "question": "Where is the staging environment?",   "value_type": "env_url"},
    ],
    "temporal": [
        {"text": "My birthday is {value}.",                "question": "When is my birthday?",             "value_type": "date"},
        {"text": "The meeting is scheduled for {value}.",  "question": "When is the meeting scheduled?",   "value_type": "date"},
        {"text": "I started this project on {value}.",     "question": "When did I start this project?",   "value_type": "date"},
        {"text": "The deadline is {value}.",               "question": "When is the deadline?",            "value_type": "date"},
        {"text": "I have been working here since {value}.", "question": "Since when have I been working here?", "value_type": "date"},
        {"text": "The conference is on {value}.",          "question": "When is the conference?",          "value_type": "date"},
    ],
    "spatial": [
        {"text": "I live in {value}.",                     "question": "Where do I live?",             "value_type": "city"},
        {"text": "My office is located in {value}.",       "question": "Where is my office?",          "value_type": "city"},
        {"text": "I grew up in {value}.",                  "question": "Where did I grow up?",         "value_type": "city"},
        {"text": "The server is hosted in {value}.",       "question": "Where is the server hosted?",  "value_type": "region"},
        {"text": "The next meeting will be held in {value}.", "question": "Where will the next meeting be held?", "value_type": "city"},
    ],
    "numerical": [
        {"text": "The budget for this project is {value}.",     "question": "What is the project budget?",    "value_type": "budget"},
        {"text": "There are {value} team members in total.",    "question": "How many team members are there?", "value_type": "count"},
        {"text": "The target is to reach {value} users.",       "question": "What is the user target?",       "value_type": "target"},
        {"text": "My phone number ends in {value}.",            "question": "What does my phone number end in?", "value_type": "digits"},
        {"text": "The access code is {value}.",                 "question": "What is the access code?",       "value_type": "code"},
    ],
}

# ── Value pools ─────────────────────────────────────────────────────────────

_VALUE_POOLS: dict[str, list[str]] = {
    "name":       ["Nilina", "Priya", "James", "Sarah", "Alex", "Chen", "Maria", "David", "Emma", "Kai", "Yuki", "Amara"],
    "age":        ["22", "24", "26", "28", "31", "33", "27", "25", "30", "35"],
    "color":      ["blue", "red", "emerald green", "purple", "teal", "orange", "navy blue", "coral", "silver"],
    "car":        ["Nissan Tiida", "Toyota Corolla", "Honda Civic", "Ford Focus", "Mazda 3", "Kia Rio", "Volkswagen Golf", "Hyundai i20"],
    "subject":    ["Data Science", "Computer Science", "Psychology", "Economics", "Physics", "Biology", "Software Engineering", "Mathematics"],
    "food":       ["sushi", "pasta", "tacos", "ramen", "pizza", "dumplings", "falafel", "biryani"],
    "job":        ["software engineer", "data analyst", "product manager", "UX designer", "researcher", "teacher", "consultant"],
    "number":     ["7", "13", "42", "17", "3", "21", "99", "8"],
    "language":   ["Sinhala", "Tamil", "Japanese", "Spanish", "French", "Mandarin", "German", "Portuguese"],
    "pet_name":   ["Mochi", "Luna", "Shadow", "Bella", "Max", "Kira", "Coco", "Tofu"],
    "port":       ["3000", "8080", "5432", "6379", "8000", "9000", "4200", "8443"],
    "db_name":    ["research_db", "analytics_db", "project_db", "memeval_db", "app_production", "staging_db"],
    "framework":  ["FastAPI", "Django", "React", "Next.js", "Flask", "Express", "Spring Boot", "Rails"],
    "url":        ["https://api.internal.dev", "https://staging.myapp.io", "http://localhost:8000", "https://api.prod.example.com"],
    "vcs":        ["Git with GitHub", "Git with GitLab", "Git with Bitbucket"],
    "env_url":    ["staging.example.com", "test.internal.dev", "qa.myapp.io", "uat.company.net"],
    "date":       ["March 15th", "September 3rd", "January 22nd", "July 8th", "November 12th", "April 5th", "December 1st", "June 20th"],
    "city":       ["Colombo", "London", "Sydney", "Toronto", "Singapore", "Berlin", "Tokyo", "Auckland", "Zurich", "Nairobi"],
    "region":     ["us-east-1", "eu-west-2", "ap-southeast-1", "us-central-1", "eu-central-1"],
    "budget":     ["$50,000", "$120,000", "$8,500", "$250,000", "$15,000"],
    "count":      ["6", "12", "4", "8", "15", "3", "20"],
    "target":     ["10,000", "100,000", "500", "50,000", "1,000,000"],
    "digits":     ["4271", "8803", "1194", "6650", "3327"],
    "code":       ["7734", "9182", "4455", "1023", "8881"],
}

# ── Injection wrapping phrases ───────────────────────────────────────────────

_WRAP_TEMPLATES = [
    "Oh, by the way — {fact} I keep meaning to mention that.",
    "Speaking of which, {fact} Thought I should share that.",
    "Actually, since we're chatting — {fact} Just something on my mind.",
    "I should probably mention — {fact} It's been relevant lately.",
    "Random thing I realised I haven't told you: {fact}",
    "While we're talking — {fact} Hope that's useful context.",
    "Just to share something about myself: {fact}",
    "I don't think I've mentioned this before, but {fact}",
    "On a slightly different note — {fact} Anyway, what were we saying?",
    "This reminds me — {fact} Thought it was worth saying.",
]


class FactInjector:
    """
    Generates Fact entities and injects them into conversations at specified positions.

    Two-phase process:
    1. generate_facts() — produces Fact entities with ground-truth answers.
    2. inject_into_conversation() — embeds facts as natural user messages.
    """

    def generate_facts(self, config: FactConfig) -> list[Fact]:
        """
        Generate a set of Fact entities from configuration.

        Args:
            config: Fact configuration (count, types, difficulty, seed).

        Returns:
            List of Facts ready for injection (insertion_turn = 0, set during injection).
        """
        rng = random.Random(config.seed)
        available_types = [t for t in config.types if t in FACT_TEMPLATES]
        if not available_types:
            available_types = ["personal"]

        facts: list[Fact] = []
        used_questions: set[str] = set()   # Avoid duplicate questions in one experiment

        attempts = 0
        while len(facts) < config.count and attempts < config.count * 10:
            attempts += 1
            fact_type = rng.choice(available_types)
            templates_for_type = FACT_TEMPLATES[fact_type]
            template = rng.choice(templates_for_type)

            # Avoid asking the same question twice
            if template["question"] in used_questions:
                continue
            used_questions.add(template["question"])

            value = self._generate_value(template["value_type"], rng)
            fact_text = template["text"].format(value=value)

            min_d, max_d = config.difficulty_range
            difficulty = round(rng.uniform(min_d, max_d), 2)
            importance = round(rng.uniform(0.5, 1.0), 2)

            fact = Fact(
                fact_id=str(uuid.uuid4()),
                text=fact_text,
                expected_answer=value,
                recall_question=template["question"],
                insertion_turn=0,     # Filled by inject_into_conversation()
                fact_type=FactType(fact_type) if fact_type in [e.value for e in FactType] else FactType.PERSONAL,
                difficulty=difficulty,
                importance=importance,
            )
            facts.append(fact)

        if len(facts) < config.count:
            logger.warning(
                "Could only generate %d/%d unique facts — consider adding more templates.",
                len(facts), config.count,
            )
        return facts

    def inject_into_conversation(
        self,
        conversation: GeneratedConversation,
        facts: list[Fact],
    ) -> tuple[GeneratedConversation, list[Fact]]:
        """
        Inject facts into the conversation at pre-marked injection slots.

        Args:
            conversation: Conversation with [INJECT_SLOT_N] markers in user turns.
            facts: Facts to inject (should match number of injection positions).

        Returns:
            Tuple of (modified conversation, facts with insertion_turn set).
        """
        rng = random.Random(conversation.config.seed + 1)  # Separate seed for wrapping

        injection_turns = conversation.get_injection_turns()
        if len(facts) > len(injection_turns):
            logger.warning(
                "More facts (%d) than injection slots (%d). Extra facts will be skipped.",
                len(facts), len(injection_turns),
            )
        if len(injection_turns) > len(facts):
            logger.warning(
                "More injection slots (%d) than facts (%d). Extra slots will be left as-is.",
                len(injection_turns), len(facts),
            )

        updated_facts: list[Fact] = []
        for i, (turn, fact) in enumerate(zip(injection_turns, facts)):
            wrapped = self._wrap_naturally(fact.text, rng)
            turn.user_message = wrapped
            turn.contains_injected_fact = True

            from dataclasses import replace
            updated_fact = Fact(
                fact_id=fact.fact_id,
                text=fact.text,
                expected_answer=fact.expected_answer,
                recall_question=fact.recall_question,
                insertion_turn=turn.turn_number,
                fact_type=fact.fact_type,
                difficulty=fact.difficulty,
                importance=fact.importance,
                tags=fact.tags,
                alternative_answers=fact.alternative_answers,
            )
            updated_facts.append(updated_fact)
            logger.debug(
                "Injected fact '%s' at turn %d", fact.recall_question, turn.turn_number
            )

        return conversation, updated_facts

    def _generate_value(self, value_type: str, rng: random.Random) -> str:
        """Pick a random value from the pool for a given type."""
        pool = _VALUE_POOLS.get(value_type)
        if pool:
            return rng.choice(pool)
        # Fallback: generate a plausible generic value
        return f"value-{rng.randint(100, 999)}"

    def _wrap_naturally(self, fact_text: str, rng: random.Random) -> str:
        """
        Wrap a bare fact sentence in conversational phrasing.
        Example: "My name is Nilina." → "Oh, by the way — My name is Nilina. I keep meaning to mention that."
        """
        template = rng.choice(_WRAP_TEMPLATES)
        # Ensure fact ends with a period
        if fact_text and fact_text[-1] not in ".!?":
            fact_text = fact_text + "."
        return template.format(fact=fact_text)
