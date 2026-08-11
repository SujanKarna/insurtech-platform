import json
from pathlib import Path

import numpy as np

from embedding.embedder import BGEEmbedder


class SemanticSearcher:
    """
    Simple in-memory semantic search over embedded chunks.

    This is intentionally kept simple for retrieval validation.
    Later, the same concept can be moved to Qdrant.
    """

    def __init__(
        self,
        embeddings_path: Path,
        embedder: BGEEmbedder,
    ) -> None:

        self.embeddings_path = embeddings_path
        self.embedder = embedder

        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None

        self._load_embeddings()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_embeddings(self) -> None:
        """
        Load chunks and their embeddings from JSONL.
        """

        if not self.embeddings_path.exists():
            raise FileNotFoundError(
                f"Embedding file not found: "
                f"{self.embeddings_path}"
            )

        embeddings = []

        with self.embeddings_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1,
            ):

                line = line.strip()

                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at line "
                        f"{line_number}"
                    ) from exc

                if "embedding" not in chunk:
                    raise ValueError(
                        f"Missing embedding at "
                        f"line {line_number}"
                    )

                self.chunks.append(chunk)
                embeddings.append(
                    chunk["embedding"]
                )

        if not embeddings:
            raise ValueError(
                "No embeddings found."
            )

        self.embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        print(
            f"Loaded chunks    : {len(self.chunks)}"
        )

        print(
            f"Embedding shape  : "
            f"{self.embeddings.shape}"
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search for the most semantically similar chunks.
        """

        if self.embeddings is None:
            raise RuntimeError(
                "Embeddings have not been loaded."
            )

        if not query.strip():
            return []

        # --------------------------------------------------------------
        # Embed query
        # --------------------------------------------------------------

        query_embedding = self.embedder.embed_one(
            query
        )

        query_vector = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        # --------------------------------------------------------------
        # Calculate cosine similarity
        #
        # Our document embeddings and query embeddings are normalized
        # by BGEEmbedder, so cosine similarity is simply the dot product.
        # --------------------------------------------------------------

        similarities = (
            self.embeddings @ query_vector
        )

        # --------------------------------------------------------------
        # Get top-k indices
        # --------------------------------------------------------------

        top_k = min(
            top_k,
            len(self.chunks),
        )

        top_indices = np.argsort(
            similarities
        )[-top_k:][::-1]

        # --------------------------------------------------------------
        # Build results
        # --------------------------------------------------------------

        results = []

        for index in top_indices:

            chunk = self.chunks[index]

            result = {
                "score": float(
                    similarities[index]
                ),
                "chunk_id": chunk["chunk_id"],
                "section_number": (
                    chunk["section_number"]
                ),
                "section_title": (
                    chunk["section_title"]
                ),
                "section_path": (
                    chunk["section_path"]
                ),
                "page_start": (
                    chunk["page_start"]
                ),
                "page_end": (
                    chunk["page_end"]
                ),
                "text": chunk["text"],
            }

            results.append(result)

        return results