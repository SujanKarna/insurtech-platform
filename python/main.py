from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

from config.settings import (
    GDV_AUB_RAW_PATH,
    GDV_AUB_URL,
    GDV_AUB_CHUNKS_PATH
)


# ============================================================================
# Extraction
# ============================================================================

from etl.extract.downloader import download_document
from etl.extract.pdf_extractor import extract_document


# ============================================================================
# Transformation
# ============================================================================

from etl.transform.zone_detector import detect_zones
from etl.transform.zone_extractor import extract_zone
from etl.transform.structure_analyzer import analyze_structure
from etl.transform.chunker import create_chunks

# ============================================================================
# Models
# ============================================================================

from models.document_zone import DocumentZone

# ============================================================================
# Load
# ============================================================================

from etl.load.chunk_writer import write_chunks_jsonl

# ============================================================================
# Inspection utilities
# ============================================================================

def get_block_preview(block) -> str:
    """
    Return a compact text preview of a raw PDF block.

    This is only a development/inspection utility.
    It does not modify the original block.
    """

    text = ""

    for line in block.lines:

        for span in line.spans:
            text += span.text

    # Collapse multiple whitespace characters.
    text = " ".join(text.split())

    # Keep terminal output manageable.
    if len(text) > 120:
        text = text[:117] + "..."

    return text


def inspect_font_sizes(document) -> None:
    """
    Print font-size and font-style statistics.

    Useful while developing the PDF structural analyzer.
    """

    font_stats = {}

    for page in document.pages:

        for block in page.blocks:

            for line in block.lines:

                for span in line.spans:

                    key = (
                        round(span.font_size, 2),
                        span.font_name,
                        span.is_bold,
                        span.is_italic,
                    )

                    font_stats[key] = (
                        font_stats.get(key, 0) + 1
                    )

    print("\nFont statistics:")
    print("-" * 100)

    sorted_stats = sorted(
        font_stats.items(),
        key=lambda item: (
            item[0][0],
            item[0][1],
        ),
    )

    for (
        font_size,
        font_name,
        is_bold,
        is_italic,
    ), count in sorted_stats:

        print(
            f"Size={font_size:5.2f} | "
            f"Font={font_name:<30} | "
            f"Bold={str(is_bold):<5} | "
            f"Italic={str(is_italic):<5} | "
            f"Count={count}"
        )

    print("-" * 100)


def inspect_pages(document) -> None:
    """
    Print a compact overview of every page.

    This is useful for inspecting the raw PDF extraction
    and debugging the zone detector.
    """

    print("\nPage structure:")
    print("=" * 100)

    for page in document.pages:

        print(
            f"\nPAGE {page.page_number}"
        )

        print(
            f"Blocks: {len(page.blocks)}"
        )

        for block_index, block in enumerate(
            page.blocks[:5]
        ):

            text = get_block_preview(block)

            print(
                f"  Block {block_index}: {text}"
            )

        if len(page.blocks) > 5:

            print(
                f"  ... "
                f"{len(page.blocks) - 5} more blocks"
            )

    print("\n" + "=" * 100)


def print_structure(
    sections,
    indent: int = 0,
) -> None:
    """
    Recursively print the detected document hierarchy.

    Example:

        [L1] 1 Was ist versichert?
          [L2] 1.1 Grundsatz
          [L2] 1.2 Geltungsbereich
            ...
    """

    for section in sections:

        prefix = "  " * indent

        print(
            f"{prefix}"
            f"[L{section.level}] "
            f"{section.number} "
            f"{section.title}"
            f" (page {section.page_number})"
        )

        if section.content:

            print(
                f"{prefix}  "
                f"Content blocks: "
                f"{len(section.content)}"
            )

        if section.children:

            print_structure(
                section.children,
                indent + 1,
            )


# ============================================================================
# Document statistics
# ============================================================================

def calculate_document_statistics(document) -> dict:
    """
    Calculate basic extraction statistics.

    Returns:
        Dictionary containing page, block, line and span counts.
    """

    total_blocks = 0
    total_lines = 0
    total_spans = 0

    for page in document.pages:

        total_blocks += len(page.blocks)

        for block in page.blocks:

            total_lines += len(block.lines)

            for line in block.lines:

                total_spans += len(line.spans)

    return {
        "pages": len(document.pages),
        "blocks": total_blocks,
        "lines": total_lines,
        "spans": total_spans,
    }

def inspect_chunks(
    chunks,
    limit: int = 10,
) -> None:
    """
    Print a small sample of generated chunks.
    """

    print("\nChunk preview:")
    print("=" * 100)

    for chunk in chunks[:limit]:

        print(
            f"\nChunk ID    : {chunk.chunk_id}"
        )

        print(
            f"Index      : {chunk.chunk_index}"
        )

        print(
            f"Pages      : "
            f"{chunk.page_start}-{chunk.page_end}"
        )

        print(
            f"Section    : "
            f"{chunk.section_number}"
        )

        print(
            f"Title      : "
            f"{chunk.section_title}"
        )

        print(
            "Path       :"
        )

        for path_item in chunk.section_path:

            print(
                f"  → {path_item}"
            )

        print(
            f"Text chars : {len(chunk.text)}"
        )

        print(
            "Text:"
        )

        print(
            chunk.text[:1000]
        )

        print("-" * 100)

# ============================================================================
# Pipeline
# ============================================================================

def run_pipeline() -> None:
    """
    Run the current document ingestion pipeline.

    Current pipeline:

        1. Download source document
        2. Store provenance
        3. Extract PDF
        4. Detect document zones
        5. Extract MAIN_CONTENT
        6. Analyze document structure

    Chunking, embeddings and LLM integration come later.
    """

    print("\nStarting insurance document pipeline...")

    # ========================================================================
    # STEP 1
    # Download source document
    # ========================================================================

    print("\n[1/5] Downloading GDV AUB document...")

    provenance = download_document(
        url=GDV_AUB_URL,
        destination=GDV_AUB_RAW_PATH,
    )

    print(
        f"Document : {provenance.file_name}"
    )

    print(
        f"Location : {provenance.file_path}"
    )

    print(
        f"Size     : {provenance.file_size} bytes"
    )

    print(
        f"SHA-256  : {provenance.sha256}"
    )

    # ========================================================================
    # STEP 2
    # Extract PDF
    # ========================================================================

    print("\n[2/5] Extracting PDF...")

    document = extract_document(
        provenance=provenance,
    )

    statistics = calculate_document_statistics(
        document
    )

    print(
        f"Pages extracted : {statistics['pages']}"
    )

    print(
        f"Blocks extracted: {statistics['blocks']}"
    )

    print(
        f"Lines extracted : {statistics['lines']}"
    )

    print(
        f"Spans extracted : {statistics['spans']}"
    )

    # ------------------------------------------------------------------------
    # Optional development inspection
    # ------------------------------------------------------------------------

    # Uncomment when debugging PDF extraction.
    #
    # inspect_font_sizes(document)
    #
    # inspect_pages(document)

    # ========================================================================
    # STEP 3
    # Detect document zones
    # ========================================================================

    print("\n[3/5] Detecting document zones...")

    zones = detect_zones(
        document
    )

    print("\nDetected document zones:")
    print("=" * 60)

    for zone in zones:

        print(
            f"{zone.zone.value:<15} "
            f"Pages {zone.start_page}-{zone.end_page} "
            f"({zone.page_count} pages)"
        )

    print("=" * 60)

    # ========================================================================
    # STEP 4
    # Extract MAIN_CONTENT
    # ========================================================================

    print("\n[4/5] Extracting main content...")

    main_content = extract_zone(
        document,
        DocumentZone.MAIN_CONTENT,
    )

    print(
        f"Main content pages : "
        f"{main_content.page_count}"
    )

    print(
        f"First page         : "
        f"{main_content.start_page}"
    )

    print(
        f"Last page          : "
        f"{main_content.end_page}"
    )

    # We don't need to print every page during normal execution.
    # Uncomment this if you want to inspect page/block counts.

    # for page in main_content.pages:
    #
    #     print(
    #         f"Page {page.page_number}: "
    #         f"{len(page.blocks)} blocks"
    #     )

    # ========================================================================
    # STEP 5
    # Analyze document structure
    # ========================================================================

    print(
        "\n[5/5] Analyzing main-content structure..."
    )

    structured_document = analyze_structure(
        main_content
    )

    print("\nDetected document structure:")
    print("=" * 100)

    print_structure(
        structured_document.sections
    )

    print("=" * 100)



    #========================================================================
    # STEP 6
    # Create structure-aware chunks
    #=======================================================================

    print("\n[6/6] Creating document chunks...")

    chunks = create_chunks(
        structured_document,
        document_id="gdv_aub",
    )

    # ========================================================================
    # STEP 7
    # Persist chunks
    # ========================================================================

    print("\n[7/7] Saving chunks...")

    chunks_path = write_chunks_jsonl(
        chunks=chunks,
        output_path=GDV_AUB_CHUNKS_PATH,
    )

    # print(
    #     f"Chunks saved : {len(chunks)}"
    # )

    # print(
    #     f"Output file  : {chunks_path}"
    # )

    # ========================================================================
    # Pipeline finished
    # ========================================================================

    print("\nPipeline finished.")


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    run_pipeline()