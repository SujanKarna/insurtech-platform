from config.settings import (
    GDV_AUB_EMBEDDINGS_PATH,
    EMBEDDING_MODEL_NAME,
)

from embedding.embedder import BGEEmbedder

from retrieval.semantic_search import (
    SemanticSearcher,
)


def print_results(
    query: str,
    results: list[dict],
) -> None:

    print()
    print("=" * 90)

    print(
        f"QUERY: {query}"
    )

    print("=" * 90)

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print()
        print(
            f"[{rank}] "
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Section: "
            f"{result['section_number']} "
            f"{result['section_title']}"
        )

        print(
            f"Pages: "
            f"{result['page_start']}-"
            f"{result['page_end']}"
        )

        print(
            "Path:"
        )

        for path_item in result[
            "section_path"
        ]:
            print(
                f"  → {path_item}"
            )

        print()
        print(
            "Text:"
        )

        print(
            result["text"]
        )

    print()


def main() -> None:

    print(
        "Starting semantic retrieval test..."
    )

    # ---------------------------------------------------------------
    # Load embedding model
    # ---------------------------------------------------------------

    embedder = BGEEmbedder(
        model_name=EMBEDDING_MODEL_NAME
    )

    # ---------------------------------------------------------------
    # Load embedded chunks
    # ---------------------------------------------------------------

    searcher = SemanticSearcher(
        embeddings_path=GDV_AUB_EMBEDDINGS_PATH,
        embedder=embedder,
    )

    # ---------------------------------------------------------------
    # Test queries
    # ---------------------------------------------------------------

    queries = [
        "Was ist ein Unfall?",
        "Wann besteht Anspruch auf Invaliditätsleistung?",
        "Wie wird der Invaliditätsgrad berechnet?",
        "Was passiert bei Vorinvalidität?",
        "Welche Unfälle sind nicht versichert?",
        "Wann wird eine Unfallrente gezahlt?",
    ]

    for query in queries:

        results = searcher.search(
            query=query,
            top_k=5,
        )

        print_results(
            query=query,
            results=results,
        )


if __name__ == "__main__":
    main()