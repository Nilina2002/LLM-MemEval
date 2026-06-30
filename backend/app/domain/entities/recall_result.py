"""
Domain entity: RecallResult.
Records the outcome of one recall test at one point in the conversation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RecallResult:
    """
    Outcome of asking the model to recall one fact at one turn.

    This is the raw measurement that feeds all downstream metrics.
    One experiment produces N_facts × N_recall_intervals RecallResults.
    """
    id: str
    experiment_id: str
    fact_id: str
    test_turn: int              # Conversation turn when this test was run
    question: str               # The recall question asked
    expected_answer: str        # Ground truth
    model_answer: str           # Raw model response
    is_correct: bool            # Determined by scoring engine
    similarity_score: float     # 0.0–1.0 from scoring engine
    scoring_method: str         # "exact" | "fuzzy" | "embedding" | "llm_judge"
    retrieved_context: str = "" # What memory strategy returned for this query
    prompt_tokens: int = 0
    response_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def turns_since_injection(self) -> int:
        """Distance from fact injection to recall test — key independent variable."""
        # Populated by the evaluation pipeline using fact metadata
        return self._turns_since_injection

    @turns_since_injection.setter
    def turns_since_injection(self, value: int) -> None:
        self._turns_since_injection = value
