"""Text processing utilities used across modules."""
from __future__ import annotations
import re


def normalize_answer(text: str) -> str:
    """Lowercase, strip whitespace, remove punctuation for comparison."""
    return re.sub(r"[^\w\s]", "", text.strip().lower())


def truncate(text: str, max_chars: int = 200) -> str:
    """Truncate text to max_chars with ellipsis."""
    return text if len(text) <= max_chars else text[:max_chars - 3] + "..."


def count_words(text: str) -> int:
    return len(text.split())


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
