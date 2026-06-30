"""
RAG Memory Strategy backed by ChromaDB.
Embeds every conversation message and retrieves the most semantically relevant
fragments at query time. Tests vector-search-based memory.
"""
from __future__ import annotations
from typing import Any

from app.strategies.base import MemoryStrategy
from app.domain.entities.message import Message


class ChromaRAGStrategy(MemoryStrategy):
    """
    Retrieval-Augmented Generation memory using ChromaDB.
    Embeds each message into a vector store and retrieves top-K at recall time.
    """

    def __init__(
        self,
        collection_name: str = "memeval_rag",
        top_k: int = 5,
        embedding_model: str = "all-MiniLM-L6-v2",
        persist_dir: str = "./chroma_data",
    ) -> None:
        self._collection_name = collection_name
        self._top_k = top_k
        self._embedding_model = embedding_model
        self._persist_dir = persist_dir
        self._client = None       # chromadb.Client — initialized lazily
        self._collection = None
        self._doc_count: int = 0

    def _get_collection(self):
        """Lazy-initialize ChromaDB client and collection."""
        if self._client is None:
            # TODO: implement — import chromadb and create/get collection
            raise NotImplementedError("ChromaDB initialization not yet implemented.")
        return self._collection

    @property
    def name(self) -> str:
        return "chroma_rag"

    @property
    def description(self) -> str:
        return "Vector-search memory using ChromaDB. Retrieves semantically relevant turns."

    def build_context(self, messages: list[Message], query: str | None = None) -> str:
        if query is None:
            return ""
        results = self.retrieve(query, top_k=self._top_k)
        if not results:
            return ""
        return "Relevant past context:\n" + "\n---\n".join(results)

    def update_memory(self, message: Message) -> None:
        # TODO: implement — embed message.content and upsert into ChromaDB collection
        self._doc_count += 1
        raise NotImplementedError

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        # TODO: implement — query ChromaDB collection with embedding
        raise NotImplementedError

    def clear(self) -> None:
        # TODO: implement — delete and recreate the collection
        self._doc_count = 0

    def get_memory_stats(self) -> dict[str, Any]:
        return {
            "collection_name": self._collection_name,
            "document_count": self._doc_count,
            "top_k": self._top_k,
        }
