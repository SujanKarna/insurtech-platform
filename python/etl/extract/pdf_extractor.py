import pymupdf

from models.provenance import DocumentProvenance
from models.raw_block import RawBlock
from models.raw_document import RawDocument
from models.raw_line import RawLine
from models.raw_page import RawPage
from models.raw_span import RawSpan


def extract_document(
    provenance: DocumentProvenance,
) -> RawDocument:
    """
    Extract the raw structure of a PDF document.

    Extraction hierarchy:

        PDF
         └── Page
              └── Block
                   └── Line
                        └── Span

    No semantic classification is performed here.
    """

    document = RawDocument(
        provenance=provenance
    )

    with pymupdf.open(provenance.file_path) as pdf:

        for page_index, pdf_page in enumerate(pdf):

            page = RawPage(
                page_number=page_index + 1,
                width=pdf_page.rect.width,
                height=pdf_page.rect.height,
            )

            blocks = pdf_page.get_text(
                "dict"
            ).get("blocks", [])

            for block_number, block_data in enumerate(blocks):

                # Ignore non-text blocks for now.
                if block_data.get("type") != 0:
                    continue

                block_bbox = block_data.get(
                    "bbox",
                    (0, 0, 0, 0),
                )

                raw_block = RawBlock(
                    block_number=block_number,
                    x0=block_bbox[0],
                    y0=block_bbox[1],
                    x1=block_bbox[2],
                    y1=block_bbox[3],
                )

                for line_number, line_data in enumerate(
                    block_data.get("lines", [])
                ):

                    line_bbox = line_data.get(
                        "bbox",
                        (0, 0, 0, 0),
                    )

                    raw_line = RawLine(
                        line_number=line_number,
                        x0=line_bbox[0],
                        y0=line_bbox[1],
                        x1=line_bbox[2],
                        y1=line_bbox[3],
                    )

                    for span_data in line_data.get(
                        "spans", []
                    ):

                        text = span_data.get(
                            "text",
                            "",
                        )

                        # Don't create empty spans.
                        if not text:
                            continue

                        span_bbox = span_data.get(
                            "bbox",
                            (0, 0, 0, 0),
                        )

                        font_name = span_data.get(
                            "font",
                            "",
                        )

                        font_size = span_data.get(
                            "size",
                            0.0,
                        )

                        flags = span_data.get(
                            "flags",
                            0,
                        )

                        raw_span = RawSpan(
                            text=text,
                            x0=span_bbox[0],
                            y0=span_bbox[1],
                            x1=span_bbox[2],
                            y1=span_bbox[3],
                            font_name=font_name,
                            font_size=font_size,
                            is_bold=_is_bold(
                                flags,
                                font_name,
                            ),
                            is_italic=_is_italic(
                                flags,
                                font_name,
                            ),
                        )

                        raw_line.spans.append(
                            raw_span
                        )

                    # Only keep lines containing text.
                    if raw_line.spans:
                        raw_block.lines.append(
                            raw_line
                        )

                # Only keep blocks containing text.
                if raw_block.lines:
                    page.blocks.append(
                        raw_block
                    )

            document.pages.append(page)

    return document


def _is_bold(
    flags: int,
    font_name: str,
) -> bool:
    """
    Determine whether a span is bold.

    PyMuPDF uses bit 4 (value 16) for the bold flag.
    Font-name detection is used as an additional fallback.
    """

    return bool(flags & 16) or "bold" in font_name.lower()


def _is_italic(
    flags: int,
    font_name: str,
) -> bool:
    """
    Determine whether a span is italic.

    PyMuPDF uses bit 1 (value 2) for italic.
    Font-name detection is used as an additional fallback.
    """

    return bool(flags & 2) or "italic" in font_name.lower()