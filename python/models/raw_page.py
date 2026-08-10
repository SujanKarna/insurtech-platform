from dataclasses import dataclass, field

from models.raw_block import RawBlock


@dataclass
class RawPage:
    """
    Represents one page of the PDF.
    """

    page_number: int

    width: float
    height: float

    blocks: list[RawBlock] = field(
        default_factory=list
    )