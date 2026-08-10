from dataclasses import dataclass, field

from models.content_type import ContentType


@dataclass
class Content:
    """
    A piece of actual document content belonging to a section.
    """

    content_type: ContentType

    text: str

    page_number: int | None = None

    block_indices: list[int] = field(
        default_factory=list
    )

    span_indices: list[int] = field(
        default_factory=list
    )