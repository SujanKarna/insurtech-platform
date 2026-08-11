import json
from pathlib import Path

from embedding.embedder import BGEEmbedder


def embed_chunks(
    chunks_path: Path,
    output_path: Path,
    embedder: BGEEmbedder,
    batch_size: int = 8,
) -> Path:
    """
    Read chunks from JSONL, generate embeddings using BGE-M3,
    and write the enriched records to another JSONL file.

    The original chunk metadata is preserved.
    """

    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {chunks_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------------
    # Read chunks
    # ---------------------------------------------------------------

    chunks = []

    with chunks_path.open(
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
                    f"Invalid JSON at line {line_number} "
                    f"in {chunks_path}"
                ) from exc

            chunks.append(chunk)

    if not chunks:
        raise ValueError(
            f"No chunks found in {chunks_path}"
        )

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    # ---------------------------------------------------------------
    # Generate embeddings
    # ---------------------------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        f"Generating embeddings for "
        f"{len(texts)} chunks..."
    )

    embeddings = embedder.embed(
        texts=texts,
        batch_size=batch_size,
    )

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Number of embeddings does not match "
            "number of chunks."
        )

    # ---------------------------------------------------------------
    # Write enriched JSONL
    # ---------------------------------------------------------------

    print(
        f"Writing embeddings to: {output_path}"
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            record = {
                **chunk,

                "embedding_model": (
                    embedder.model_name
                ),

                "embedding_dimension": (
                    embedder.dimension
                ),

                "embedding": embedding,
            }

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print(
        f"Embeddings written: {len(embeddings)}"
    )

    return output_path