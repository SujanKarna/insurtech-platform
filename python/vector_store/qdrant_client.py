from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from config.settings import (
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION_NAME,
    QDRANT_VECTOR_SIZE,
)


class QdrantVectorStore:

    def __init__(self):

        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.collection_name = QDRANT_COLLECTION_NAME

    def create_collection(self):

        collections = self.client.get_collections()

        existing_collections = {
            collection.name
            for collection in collections.collections
        }

        if self.collection_name in existing_collections:

            print(
                f"Collection '{self.collection_name}' "
                "already exists."
            )

            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=QDRANT_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created collection: "
            f"{self.collection_name}"
        )