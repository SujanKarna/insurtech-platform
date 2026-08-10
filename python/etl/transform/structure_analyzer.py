import re

from models.section import Section
from models.section_type import SectionType
from models.content import Content
from models.content_type import ContentType
from models.document_section import DocumentSection


# ---------------------------------------------------------------------------
# Numbering patterns
# ---------------------------------------------------------------------------

# Examples:
#
# 1 Was ist versichert?
# 1.1 Grundsatz
# 1.4.1 Erhöhte Kraftanstrengung
# 2.1.2.2.1 Gliedertaxe
#
# We deliberately allow a space OR no space after the number because
# PDF extraction can sometimes produce:
#
# 1.1 Grundsatz
# 1.1Grundsatz
#
# Both should be detected as structural candidates.
SECTION_PATTERN = re.compile(
    r"^\s*"
    r"(?P<number>\d+(?:\.\d+)*)"
    r"\.?"
    r"\s+"
    r"(?P<title>.+?)"
    r"\s*$"
)


# Special cases such as:
#
# 4. GESTRICHEN
#
# The general pattern already catches this, but keeping the rule
# separate makes the intent explicit.
REPEALED_PATTERN = re.compile(
    r"^\s*"
    r"(?P<number>\d+(?:\.\d+)*)"
    r"\.?"
    r"\s+"
    r"(?P<title>gestrichen)"
    r"\s*$",
    re.IGNORECASE,
)


def _extract_block_text(block) -> str:
    """
    Reconstruct the text contained in a raw PDF block.

    The original span objects are not modified.
    """

    parts = []

    for line in block.lines:
        for span in line.spans:
            if span.text:
                parts.append(span.text)

    return " ".join(parts).strip()


def _detect_section_heading(text: str):
    """
    Check whether a block looks like a numbered section heading.

    Returns:
        (number, title, level)
        or
        None
    """

    if not text:
        return None

    # ---------------------------------------------------------------
    # Repealed section
    # ---------------------------------------------------------------

    match = REPEALED_PATTERN.match(text)

    if match:
        number = match.group("number")
        title = match.group("title").strip()

        level = number.count(".") + 1

        return number, title, level

    # ---------------------------------------------------------------
    # Normal numbered section
    # ---------------------------------------------------------------

    match = SECTION_PATTERN.match(text)

    if not match:
        return None

    number = match.group("number")
    title = match.group("title").strip()

    level = number.count(".") + 1

    return number, title, level


def _section_type(level: int) -> SectionType:
    """
    Convert a numerical hierarchy level into a broad section type.

    We intentionally do not create SUBSUBSECTION,
    SUBSUBSUBSECTION, etc. enums.

    The actual hierarchy depth is represented by `level`.
    """

    if level == 1:
        return SectionType.SECTION

    if level == 2:
        return SectionType.SUBSECTION

    if level >= 3:
        return SectionType.SUBSECTION

    return SectionType.UNKNOWN


def _create_content(
    block,
    page_number: int,
    block_index: int,
) -> Content:
    """
    Convert a raw block into a temporary Content object.

    At this stage everything that is not identified as a heading
    is treated as PARAGRAPH.

    More detailed classification will be added later for:
        - lists
        - examples
        - notes
        - tables
    """

    text = _extract_block_text(block)

    return Content(
        content_type=ContentType.PARAGRAPH,
        text=text,
        page_number=page_number,
        block_indices=[block_index],
    )


def analyze_structure(
    document_section: DocumentSection,
) -> DocumentSection:
    """
    Analyze the structure of a MAIN_CONTENT DocumentSection.

    Current responsibilities:

    1. Identify numbered headings.
    2. Determine their hierarchy level.
    3. Create Section objects.
    4. Build parent-child relationships.
    5. Attach non-heading blocks as Content.

    The original pages and blocks are NOT modified.
    """

    # -----------------------------------------------------------------------
    # Root sections
    # -----------------------------------------------------------------------

    root_sections: list[Section] = []

    # Stack contains the most recent section at each hierarchy level.
    #
    # Example:
    #
    # level 1 → Section 1
    # level 2 → Section 1.4
    # level 3 → Section 1.4.1
    #
    section_stack: list[Section] = []

    # -----------------------------------------------------------------------
    # Process pages
    # -----------------------------------------------------------------------

    for page in document_section.pages:

        for block_index, block in enumerate(page.blocks):

            text = _extract_block_text(block)

            if not text:
                continue

            heading = _detect_section_heading(
                text
            )

            # ===============================================================
            # HEADING
            # ===============================================================

            if heading:

                number, title, level = heading

                section = Section(
                    section_type=_section_type(level),
                    number=number,
                    title=title,
                    level=level,
                    page_number=page.page_number,
                )

                # -----------------------------------------------------------
                # Find parent
                # -----------------------------------------------------------

                while (
                    section_stack
                    and section_stack[-1].level >= level
                ):
                    section_stack.pop()

                if section_stack:

                    parent = section_stack[-1]

                    section.parent = parent

                    parent.children.append(
                        section
                    )

                else:

                    root_sections.append(
                        section
                    )

                # -----------------------------------------------------------
                # Update hierarchy stack
                # -----------------------------------------------------------

                section_stack.append(
                    section
                )

            # ===============================================================
            # CONTENT
            # ===============================================================

            else:

                content = _create_content(
                    block=block,
                    page_number=page.page_number,
                    block_index=block_index,
                )

                # Ignore content that somehow appears before
                # the first structural section.
                #
                # We don't want to silently attach introductory material
                # to an arbitrary section.
                if section_stack:

                    current_section = section_stack[-1]

                    current_section.content.append(
                        content
                    )

                else:

                    # For now we simply skip blocks before the first
                    # recognized heading.
                    #
                    # We will later decide whether these should become
                    # PART/front-matter nodes.
                    continue

    # -----------------------------------------------------------------------
    # Store the generated structure
    # -----------------------------------------------------------------------

    document_section.sections = root_sections

    return document_section