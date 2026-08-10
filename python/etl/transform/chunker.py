from models.chunk import DocumentChunk
from models.section import Section
from models.document_section import DocumentSection


# ============================================================================
# Configuration
# ============================================================================

# Maximum approximate number of characters in a chunk.
#
# We intentionally use characters for now rather than tokens because:
#
# 1. We are not tied to a specific embedding model yet.
# 2. It keeps the chunker model-independent.
# 3. We can introduce token-aware splitting later if needed.
DEFAULT_MAX_CHUNK_SIZE = 1500


# Small amount of overlap when a section needs to be split.
#
# This helps avoid losing context at chunk boundaries.
DEFAULT_CHUNK_OVERLAP = 200


# ============================================================================
# Text helpers
# ============================================================================

def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace without performing semantic cleaning.

    We deliberately do NOT:
        - correct spelling
        - join broken words
        - rewrite sentences
        - remove legal terminology
    """

    return " ".join(
        text.split()
    )


def _content_text(content) -> str:
    """
    Extract normalized text from a Content object.
    """

    if not content.text:
        return ""

    return _normalize_whitespace(
        content.text
    )


# ============================================================================
# Section hierarchy
# ============================================================================

def _build_section_path(
    section: Section,
) -> list[str]:
    """
    Build the complete hierarchy path for a section.

    Example:

        [
            "2 Welche Leistungsarten können vereinbart werden?",
            "2.1 Invaliditätsleistung",
            "2.1.1 Voraussetzungen für die Leistung",
            "2.1.1.2 Eintritt und ärztliche Feststellung der Invalidität"
        ]
    """

    path = []

    current = section

    while current is not None:

        title = current.title

        if current.number:
            title = f"{current.number} {title}"

        path.append(title)

        current = current.parent

    # Parent was collected first, so reverse it.
    path.reverse()

    return path


# ============================================================================
# Content collection
# ============================================================================

def _collect_section_content(
    section: Section,
) -> list:
    """
    Collect content belonging to a section.

    We currently keep content attached directly to the section.

    Child sections are processed separately so that their hierarchy
    remains explicit.
    """

    return section.content


# ============================================================================
# Chunk creation
# ============================================================================

def _build_context_prefix(
    section_path: list[str],
) -> str:
    """
    Build the structural context that will be prepended to chunk text.

    Example:

        Section: 2 ...
        Section: 2.1 ...
        Section: 2.1.1 ...
    """

    if not section_path:
        return ""

    return (
        "Document structure:\n"
        + "\n".join(
            section_path
        )
        + "\n\n"
    )


def _create_chunk(
    *,
    section: Section,
    section_path: list[str],
    text: str,
    chunk_index: int,
    document_id: str | None,
    page_start: int | None,
    page_end: int | None,
    source_block_indices: list[int],
) -> DocumentChunk:
    """
    Create a DocumentChunk.
    """

    section_number = section.number
    section_title = section.title

    chunk_id = (
        f"{document_id or 'document'}"
        f"_{section_number or 'root'}"
        f"_{chunk_index}"
    )

    return DocumentChunk(
        chunk_id=chunk_id,
        chunk_index=chunk_index,
        text=text,
        document_id=document_id,
        section_number=section_number,
        section_title=section_title,
        section_path=section_path,
        page_start=page_start,
        page_end=page_end,
        source_block_indices=source_block_indices,
    )


# ============================================================================
# Splitting
# ============================================================================

def _split_text(
    text: str,
    max_size: int,
    overlap: int,
) -> list[str]:
    """
    Split large text into approximately max_size character chunks.

    Splitting happens on word boundaries.

    The overlap is character-based and deliberately simple.
    """

    if len(text) <= max_size:

        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + max_size,
            text_length,
        )

        # ---------------------------------------------------------------
        # Try to end on a word boundary.
        # ---------------------------------------------------------------

        if end < text_length:

            boundary = text.rfind(
                " ",
                start,
                end,
            )

            if boundary > start:

                end = boundary

        chunk = text[
            start:end
        ].strip()

        if chunk:

            chunks.append(
                chunk
            )

        # ---------------------------------------------------------------
        # Move forward while keeping overlap.
        # ---------------------------------------------------------------

        if end >= text_length:
            break

        next_start = end - overlap

        # Prevent infinite loops.
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


# ============================================================================
# Section processing
# ============================================================================

def _chunk_section(
    section: Section,
    *,
    document_id: str | None,
    max_chunk_size: int,
    overlap: int,
    chunk_index_start: int,
) -> tuple[list[DocumentChunk], int]:
    """
    Convert one section into chunks.

    Returns:

        chunks
        next chunk index
    """

    chunks = []

    section_path = _build_section_path(
        section
    )

    context_prefix = _build_context_prefix(
        section_path
    )

    contents = _collect_section_content(
        section
    )

    if not contents:

        return chunks, chunk_index_start

    # ------------------------------------------------------------------
    # Build content units
    #
    # We first preserve the individual Content objects.
    # Then we combine them until the maximum chunk size is reached.
    # ------------------------------------------------------------------

    current_parts = []
    current_length = 0

    current_pages = []
    current_blocks = []

    chunk_index = chunk_index_start

    def flush_current_chunk():

        nonlocal current_parts
        nonlocal current_length
        nonlocal current_pages
        nonlocal current_blocks
        nonlocal chunk_index

        if not current_parts:
            return

        body = "\n\n".join(
            current_parts
        )

        full_text = (
            context_prefix
            + body
        )

        page_start = (
            min(current_pages)
            if current_pages
            else None
        )

        page_end = (
            max(current_pages)
            if current_pages
            else None
        )

        chunk = _create_chunk(
            section=section,
            section_path=section_path,
            text=full_text,
            chunk_index=chunk_index,
            document_id=document_id,
            page_start=page_start,
            page_end=page_end,
            source_block_indices=list(
                current_blocks
            ),
        )

        chunks.append(
            chunk
        )

        chunk_index += 1

        current_parts = []
        current_length = 0
        current_pages = []
        current_blocks = []

    # ------------------------------------------------------------------
    # Process each content block
    # ------------------------------------------------------------------

    for content in contents:

        text = _content_text(
            content
        )

        if not text:
            continue

        # ---------------------------------------------------------------
        # A single content block is already too large.
        #
        # Split it separately.
        # ---------------------------------------------------------------

        if len(text) > max_chunk_size:

            flush_current_chunk()

            split_parts = _split_text(
                text,
                max_size=max_chunk_size,
                overlap=overlap,
            )

            for part in split_parts:

                full_text = (
                    context_prefix
                    + part
                )

                chunk = _create_chunk(
                    section=section,
                    section_path=section_path,
                    text=full_text,
                    chunk_index=chunk_index,
                    document_id=document_id,
                    page_start=content.page_number,
                    page_end=content.page_number,
                    source_block_indices=list(
                        content.block_indices
                    ),
                )

                chunks.append(
                    chunk
                )

                chunk_index += 1

            continue

        # ---------------------------------------------------------------
        # Would adding this content exceed the chunk size?
        # ---------------------------------------------------------------

        additional_length = (
            len(text)
            + (
                2
                if current_parts
                else 0
            )
        )

        if (
            current_parts
            and
            current_length + additional_length
            > max_chunk_size
        ):

            flush_current_chunk()

        # ---------------------------------------------------------------
        # Add content to current chunk.
        # ---------------------------------------------------------------

        current_parts.append(
            text
        )

        current_length += (
            len(text)
            + (
                2
                if len(current_parts) > 1
                else 0
            )
        )

        current_pages.append(
            content.page_number
        )

        current_blocks.extend(
            content.block_indices
        )

    # Flush final chunk.
    flush_current_chunk()

    return chunks, chunk_index


# ============================================================================
# Main chunker
# ============================================================================

def create_chunks(
    document_section: DocumentSection,
    *,
    document_id: str | None = None,
    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Create structure-aware chunks from a structured document.

    Important:

    The chunker does NOT try to understand the legal meaning
    of the document.

    It only preserves:

        - section hierarchy
        - section path
        - content
        - page numbers
        - source block references

    This makes the output suitable for later embedding.
    """

    chunks = []

    chunk_index = 0

    # ------------------------------------------------------------------
    # Recursively process sections.
    # ------------------------------------------------------------------

    def process_section(section: Section):

        nonlocal chunk_index

        section_chunks, chunk_index = _chunk_section(
            section,
            document_id=document_id,
            max_chunk_size=max_chunk_size,
            overlap=overlap,
            chunk_index_start=chunk_index,
        )

        chunks.extend(
            section_chunks
        )

        # --------------------------------------------------------------
        # Process children independently.
        #
        # This is important because each child receives its own
        # section path and metadata.
        # --------------------------------------------------------------

        for child in section.children:

            process_section(
                child
            )

    # ------------------------------------------------------------------
    # Start with root sections.
    # ------------------------------------------------------------------

    for section in document_section.sections:

        process_section(
            section
        )

    return chunks