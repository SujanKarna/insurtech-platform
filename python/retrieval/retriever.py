from dataclasses import dataclass
from typing import List

from embedding.embedder import BGEEmbedder
from vector_store.qdrant_retriever import QdrantRetriever


@dataclass
class RetrievalResult:
    score: float
    chunk_id: str
    text: str
    document_id: str
    section_number: str
    section_title: str
    section_path: List[str]
    page_start: int
    page_end: int
    source_block_indices: List[int]


class Retriever:
    """
    High-level retrieval service.

    Converts a natural-language query into an embedding
    and retrieves the most relevant chunks from Qdrant.
    """

    def __init__(self):
        self.embedder = BGEEmbedder()
        self.vector_store = QdrantRetriever()

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: Natural-language user query.
            top_k: Number of chunks to retrieve.

        Returns:
            List of RetrievalResult objects.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        # 1. Convert query to embedding
        query_embedding = self.embedder.embed(query)

        # 2. Search Qdrant
        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
        )

        # 3. Convert Qdrant results into application-level objects
        retrieved_chunks = []

        for result in results:

            payload = result.payload or {}

            retrieved_chunks.append(
                RetrievalResult(
                    score=float(result.score),
                    chunk_id=payload.get("chunk_id", ""),
                    text=payload.get("text", ""),
                    document_id=payload.get("document_id", ""),
                    section_number=payload.get("section_number", ""),
                    section_title=payload.get("section_title", ""),
                    section_path=payload.get("section_path", []),
                    page_start=payload.get("page_start", 0),
                    page_end=payload.get("page_end", 0),
                    source_block_indices=payload.get(
                        "source_block_indices",
                        [],
                    ),
                )
            )

        return retrieved_chunks