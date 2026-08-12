from qdrant_client import QdrantClient

from config.settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION_NAME,
)


class QdrantRetriever:

    def __init__(self):
        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.collection = QDRANT_COLLECTION_NAME

    def search(self, query_vector, top_k=5):
        """
        Search Qdrant using an already generated query embedding.

        Args:
            query_vector: 1024-dimensional embedding.
            top_k: Number of results to return.

        Returns:
            List of Qdrant search results.
        """

        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        return results.points