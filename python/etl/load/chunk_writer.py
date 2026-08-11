import json
from pathlib import Path

from models.chunk import DocumentChunk


def _chunk_to_dict(
    chunk: DocumentChunk,
) -> dict:
    """
    Convert a DocumentChunk into a JSON-serializable dictionary.
    """

    return {
        "chunk_id": chunk.chunk_id,
        "chunk_index": chunk.chunk_index,

        "text": chunk.text,

        "document_id": chunk.document_id,

        "section_number": chunk.section_number,
        "section_title": chunk.section_title,
        "section_path": chunk.section_path,

        "page_start": chunk.page_start,
        "page_end": chunk.page_end,

        "source_block_indices": (
            chunk.source_block_indices
        ),
    }


def write_chunks_jsonl(
    chunks: list[DocumentChunk],
    output_path: Path,
) -> Path:
    """
    Write document chunks to a JSONL file.

    Each chunk is stored as one JSON object per line.

    Existing files are overwritten so that each pipeline run
    produces a deterministic output.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        for chunk in chunks:

            record = _chunk_to_dict(
                chunk
            )

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )

    return output_path