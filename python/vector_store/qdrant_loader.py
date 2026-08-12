import json

from pathlib import Path

from qdrant_client.models import PointStruct

from config.settings import (
    GDV_AUB_EMBEDDINGS_PATH,
)

from vector_store.qdrant_client import (
    QdrantVectorStore,
)


class QdrantLoader:

    def __init__(self):

        self.store = QdrantVectorStore()

    def load_jsonl(
        self,
        jsonl_path: Path = GDV_AUB_EMBEDDINGS_PATH,
    ) -> int:

        if not jsonl_path.exists():

            raise FileNotFoundError(
                f"Embedding file not found: "
                f"{jsonl_path}"
            )

        points = []

        with jsonl_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                if not line.strip():
                    continue

                data = json.loads(line)

                point = PointStruct(
                    id=data["chunk_index"],

                    vector=data["embedding"],

                    payload={
                        "chunk_id": data["chunk_id"],
                        "chunk_index": data["chunk_index"],
                        "text": data["text"],
                        "document_id": data["document_id"],
                        "section_number": data[
                            "section_number"
                        ],
                        "section_title": data[
                            "section_title"
                        ],
                        "section_path": data[
                            "section_path"
                        ],
                        "page_start": data["page_start"],
                        "page_end": data["page_end"],
                        "source_block_indices": data[
                            "source_block_indices"
                        ],
                        "embedding_model": data[
                            "embedding_model"
                        ],
                    },
                )

                points.append(point)

        if not points:

            print("No embeddings found.")

            return 0

        self.store.create_collection()

        self.store.client.upsert(
            collection_name=self.store.collection_name,
            points=points,
        )

        print(
            f"Inserted {len(points)} vectors into "
            f"'{self.store.collection_name}'."
        )

        return len(points)