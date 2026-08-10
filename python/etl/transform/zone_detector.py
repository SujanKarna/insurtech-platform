import re

from models.document_zone import DocumentZone
from models.raw_document import RawDocument
from models.raw_page import RawPage
from models.zone import DocumentZoneRange


def detect_zones(
    document: RawDocument,
) -> list[DocumentZoneRange]:
    """
    Detect the high-level zones of the document.

    Expected structure:

        INTRO
        TOC
        MAIN_CONTENT
    """

    if not document.pages:
        return []

    toc_page = find_toc_page(document)

    if toc_page is None:
        raise ValueError(
            "Could not identify the table of contents."
        )

    main_content_page = find_main_content_start(
        document,
        start_page=toc_page + 1,
    )

    if main_content_page is None:
        raise ValueError(
            "Could not identify the beginning of the main content."
        )

    zones: list[DocumentZoneRange] = []

    # ------------------------------------------------------------------
    # INTRO
    # ------------------------------------------------------------------

    if toc_page > 1:
        zones.append(
            DocumentZoneRange(
                zone=DocumentZone.INTRO,
                start_page=document.pages[0].page_number,
                end_page=toc_page - 1,
            )
        )

    # ------------------------------------------------------------------
    # TOC
    # ------------------------------------------------------------------

    zones.append(
        DocumentZoneRange(
            zone=DocumentZone.TOC,
            start_page=toc_page,
            end_page=main_content_page - 1,
        )
    )

    # ------------------------------------------------------------------
    # MAIN CONTENT
    # ------------------------------------------------------------------

    zones.append(
        DocumentZoneRange(
            zone=DocumentZone.MAIN_CONTENT,
            start_page=main_content_page,
            end_page=document.pages[-1].page_number,
        )
    )

    return zones


# ============================================================================
# TABLE OF CONTENTS
# ============================================================================


def find_toc_page(
    document: RawDocument,
) -> int | None:
    """
    Find the page containing the 'Inhaltsverzeichnis' heading.

    Detection is performed block-by-block because the PDF
    extraction may preserve different text fragments separately.
    """


    for page in document.pages:

        for block in page.blocks:
            
            text = get_block_text(block)
            # print(f"PAGE {page.page_number}: "f"{repr(text)}")
            normalized = normalize_text(text)

            if normalized == "Inhaltsverzeichnis":
                return page.page_number

            # Also allow the word to occur inside a larger block.
            if "inhaltsverzeichnis" in normalized:
                return page.page_number

    return None


# ============================================================================
# MAIN CONTENT
# ============================================================================


def find_main_content_start(
    document: RawDocument,
    start_page: int,
) -> int | None:
    """
    Find the first page of the actual AUB content.

    We start searching after the TOC because the TOC itself
    contains entries such as:

        1 Was ist versichert?
        1.1 Grundsatz

    The first real content page contains these headings
    followed by actual explanatory text.
    """

    for page in document.pages:

        if page.page_number < start_page:
            continue

        if is_main_content_page(page):
            return page.page_number

    return None


def is_main_content_page(
    page: RawPage,
) -> bool:
    """
    Determine whether a page contains the beginning
    of the main insurance conditions.

    For the current AUB document we expect:

        1 Was ist versichert?
        1.1 Grundsatz

    followed by body text.
    """

    block_texts = [
        normalize_text(
            get_block_text(block)
        )
        for block in page.blocks
    ]

    # Remove empty blocks.
    block_texts = [
        text
        for text in block_texts
        if text
    ]

    if not block_texts:
        return False

    has_first_section = any(
        matches_first_section(text)
        for text in block_texts
    )

    if not has_first_section:
        return False

    has_first_subsection = any(
        matches_first_subsection(text)
        for text in block_texts
    )

    if not has_first_subsection:
        return False

    if not has_body_text_after_heading(
        block_texts
    ):
        return False

    return True


def matches_first_section(
    text: str,
) -> bool:
    """
    Match:

        1 Was ist versichert?

    The PDF sometimes contains slightly different
    spacing around the question mark.
    """

    pattern = (
        r"^1\s+was\s+ist\s+versichert\s*\??$"
    )

    return bool(
        re.match(
            pattern,
            text,
            re.IGNORECASE,
        )
    )


def matches_first_subsection(
    text: str,
) -> bool:
    """
    Match:

        1.1 Grundsatz
    """

    pattern = (
        r"^1\.1\s+grundsatz$"
    )

    return bool(
        re.match(
            pattern,
            text,
            re.IGNORECASE,
        )
    )


def has_body_text_after_heading(
    block_texts: list[str],
) -> bool:
    """
    Check whether actual explanatory text follows
    the '1.1 Grundsatz' heading.
    """

    for index, text in enumerate(block_texts):

        if not matches_first_subsection(text):
            continue

        following_blocks = block_texts[
            index + 1:
        ]

        for following_text in following_blocks:

            if not following_text:
                continue

            # Ignore structural headings.
            if is_structural_heading(
                following_text
            ):
                continue

            # Actual paragraph text should be
            # reasonably long.
            if len(following_text) >= 40:
                return True

    return False


# ============================================================================
# TEXT HELPERS
# ============================================================================


def get_block_text(
    block,
) -> str:
    """
    Extract all text from a RawBlock.
    """

    parts = []

    for line in block.lines:

        for span in line.spans:

            if span.text:
                parts.append(
                    span.text
                )

    return "".join(parts)


def normalize_text(
    text: str,
) -> str:
    """
    Normalize whitespace for matching only.

    This is NOT the document text cleaner.
    """

    return " ".join(
        text.split()
    ).strip()


def is_structural_heading(
    text: str,
) -> bool:
    """
    Determine whether a block looks like a numbered
    structural heading.

    Examples:

        1 Was ist versichert?
        1.1 Grundsatz
        1.4.3 Unfälle unter Wasser
        2.1.2.2.1 Gliedertaxe
    """

    return bool(
        re.match(
            r"^\d+(?:\.\d+)*\s+",
            text,
        )
    )