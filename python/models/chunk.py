from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    """
    A structure-aware chunk ready for embedding.

    The chunk contains both the text that will be embedded and
    metadata required for retrieval and provenance.
    """

    # ------------------------------------------------------------------
    # Chunk identity
    # ------------------------------------------------------------------

    chunk_id: str

    chunk_index: int

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    text: str

    # ------------------------------------------------------------------
    # Document information
    # ------------------------------------------------------------------

    document_id: str | None = None

    # ------------------------------------------------------------------
    # Structural context
    # ------------------------------------------------------------------

    section_number: str | None = None

    section_title: str | None = None

    section_path: list[str] = field(
        default_factory=list
    )

    # ------------------------------------------------------------------
    # Source location
    # ------------------------------------------------------------------

    page_start: int | None = None

    page_end: int | None = None

    source_block_indices: list[int] = field(
        default_factory=list
    )