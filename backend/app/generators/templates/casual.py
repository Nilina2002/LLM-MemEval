"""
Casual conversation templates.
Topic sequences and turn starters for everyday chitchat conversations.
"""
from __future__ import annotations

TOPICS = [
    "weekend plans", "weather", "favorite foods", "movies", "music", "sports",
    "travel memories", "hobbies", "pets", "family", "work stress", "books",
    "TV shows", "cooking", "exercise habits", "sleep", "technology",
    "social media", "news", "childhood memories",
]

USER_STARTERS: dict[str, list[str]] = {
    "weekend plans": [
        "So what are you up to this weekend?",
        "Do you have any plans for the weekend?",
        "I'm thinking about what to do this weekend.",
    ],
    "weather": [
        "The weather's been crazy lately, hasn't it?",
        "Can you believe this heat?",
        "I love these rainy days.",
    ],
    "favorite foods": [
        "I've been really into cooking lately.",
        "What do you think about pizza?",
        "I tried this amazing restaurant yesterday.",
    ],
    # TODO: add starters for remaining topics
}

ASSISTANT_RESPONSES: dict[str, list[str]] = {
    "weekend plans": [
        "I was thinking of catching up on some reading. What about you?",
        "Maybe a hike if the weather holds up!",
        "I have some errands to run, but hopefully something fun too.",
    ],
    # TODO: add responses for remaining topics
}


def get_topics() -> list[str]:
    return TOPICS


def get_user_starter(topic: str) -> str:
    """Return a random user message for a given topic."""
    starters = USER_STARTERS.get(topic, [f"Let's talk about {topic}."])
    return starters[0]  # Index selection done by seeded RNG in the generator


def get_assistant_response(topic: str) -> str:
    """Return a random assistant response for a given topic."""
    responses = ASSISTANT_RESPONSES.get(topic, ["That's interesting! Tell me more."])
    return responses[0]
