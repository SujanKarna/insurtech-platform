from dataclasses import dataclass, field

from models.section_type import SectionType
from models.content import Content


@dataclass
class Section:
    """
    Represents a structural section of the document.
    """

    section_type: SectionType

    number: str | None

    title: str

    level: int

    page_number: int | None = None

    children: list["Section"] = field(
        default_factory=list
    )

    content: list[Content] = field(
        default_factory=list
    )

    parent: "Section | None" = field(
        default=None,
        repr=False,
    )