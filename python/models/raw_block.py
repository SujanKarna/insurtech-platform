from dataclasses import dataclass, field

from models.raw_line import RawLine


@dataclass
class RawBlock:
    """
    Represents a raw text block extracted from a PDF page.
    """

    block_number: int

    x0: float
    y0: float
    x1: float
    y1: float

    lines: list[RawLine] = field(
        default_factory=list
    )