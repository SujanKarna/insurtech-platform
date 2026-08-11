from sentence_transformers import SentenceTransformer


class BGEEmbedder:
    """
    Wrapper around the BAAI/bge-m3 embedding model.

    The model converts text into dense 1024-dimensional
    vectors suitable for semantic retrieval.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str | None = None,
    ) -> None:

        print(
            f"Loading embedding model: {model_name}"
        )

        self.model = SentenceTransformer(
            model_name,
            device=device,
        )

        self.model_name = model_name

        print(
            f"Embedding model loaded: {model_name}"
        )

    def embed(
        self,
        texts: list[str],
        batch_size: int = 8,
    ) -> list[list[float]]:
        """
        Generate dense embeddings for a list of texts.

        Returns:
            List of embedding vectors.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_one(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """
        Return embedding dimensionality.
        """

        return self.model.get_sentence_embedding_dimension()