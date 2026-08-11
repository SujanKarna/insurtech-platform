from config.settings import (
    GDV_AUB_CHUNKS_PATH,
    GDV_AUB_EMBEDDINGS_PATH,
    EMBEDDING_MODEL_NAME,
)

from embedding.embedder import BGEEmbedder

from etl.load.embedding_writer import (
    embed_chunks,
)


def main() -> None:

    print(
        "Starting chunk embedding..."
    )

    # ---------------------------------------------------------------
    # Load embedding model
    # ---------------------------------------------------------------

    embedder = BGEEmbedder(
        model_name=EMBEDDING_MODEL_NAME,
    )

    print(
        f"Model     : {embedder.model_name}"
    )

    print(
        f"Dimension : {embedder.dimension}"
    )

    # ---------------------------------------------------------------
    # Embed chunks
    # ---------------------------------------------------------------

    output_path = embed_chunks(
        chunks_path=GDV_AUB_CHUNKS_PATH,
        output_path=GDV_AUB_EMBEDDINGS_PATH,
        embedder=embedder,
        batch_size=8,
    )

    # ---------------------------------------------------------------
    # Result
    # ---------------------------------------------------------------

    print()
    print("=" * 70)

    print(
        f"Embedding file: {output_path}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()