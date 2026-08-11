from embedding.embedder import BGEEmbedder


def main() -> None:

    embedder = BGEEmbedder()

    texts = [
        "Was ist ein Unfall?",
        "Was ist eine Invaliditätsleistung?",
        "Versicherungsschutz besteht weltweit.",
    ]

    embeddings = embedder.embed(
        texts
    )

    print()
    print("=" * 60)

    print(
        f"Texts      : {len(texts)}"
    )

    print(
        f"Dimension  : {len(embeddings[0])}"
    )

    print(
        f"Vectors    : {len(embeddings)}"
    )

    print()
    print(
        "First vector:"
    )

    print(
        embeddings[0][:10]
    )

    print("=" * 60)


if __name__ == "__main__":
    main()