from dataclasses import dataclass

from models.raw_block import RawBlock


@dataclass
class CleanBlock:
    """
    Cleaned textual representation of a raw PDF block.

    The original RawBlock is retained so that the cleaned
    text can always be traced back to the source.
    """

    text: str
    source_block: RawBlock