"""
Embedding similarity scorer using sentence-transformers.
Measures semantic equivalence — catches paraphrases and synonyms.
"""
from __future__ import annotations
import numpy as np
from app.domain.interfaces.scorer import Scorer, ScoringResult


class EmbeddingSimilarityScorer(Scorer):
    """
    Encodes expected and actual answers into embedding vectors
    and computes cosine similarity. Model loaded once and cached.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None  # Lazy-loaded

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model

    @property
    def method_name(self) -> str:
        return "embedding"

    def score(self, expected: str, actual: str, threshold: float = 0.80) -> ScoringResult:
        model = self._get_model()
        embeddings = model.encode([expected, actual], normalize_embeddings=True)
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        return ScoringResult(
            score=similarity,
            is_correct=similarity >= threshold,
            method=self.method_name,
            explanation=f"Cosine similarity: {similarity:.4f} (threshold: {threshold})",
        )
