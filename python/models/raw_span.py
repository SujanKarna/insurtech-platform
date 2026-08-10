from dataclasses import dataclass


@dataclass
class RawSpan:
    """
    Represents the smallest text element extracted from a PDF.

    A span normally represents text with consistent formatting.
    """

    text: str

    x0: float
    y0: float
    x1: float
    y1: float

    font_name: str
    font_size: float

    is_bold: bool
    is_italic: bool