from embedding.embedder import BGEEmbedder
from vector_store.qdrant_retriever import QdrantRetriever


def main():

    query = "Was ist ein Unfall?"

    # Generate embedding for the query
    embedder = BGEEmbedder()

    query_embedding = embedder.embed(query)

    # Search Qdrant
    retriever = QdrantRetriever()

    results = retriever.search(
        query_vector=query_embedding,
        top_k=5,
    )

    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    for i, result in enumerate(results, start=1):

        payload = result.payload

        print(f"\n[{i}]")
        print(f"Score   : {result.score}")
        print(f"Section : {payload.get('section_number')}")
        print(f"Title   : {payload.get('section_title')}")
        print(f"Pages   : {payload.get('page_start')}-{payload.get('page_end')}")

        print("\nText:")
        print(payload.get("text"))


if __name__ == "__main__":
    main()