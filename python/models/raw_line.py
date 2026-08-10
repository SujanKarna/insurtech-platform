from dataclasses import dataclass, field

from models.raw_span import RawSpan


@dataclass
class RawLine:
    """
    Represents a single line within a PDF text block.
    """

    line_number: int

    x0: float
    y0: float
    x1: float
    y1: float

    spans: list[RawSpan] = field(
        default_factory=list
    )