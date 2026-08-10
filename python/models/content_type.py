from enum import Enum


class ContentType(str, Enum):
    """
    Types of content that can occur inside a section.
    """

    PARAGRAPH = "PARAGRAPH"

    LIST = "LIST"

    LIST_ITEM = "LIST_ITEM"

    EXAMPLE = "EXAMPLE"

    NOTE = "NOTE"

    TABLE = "TABLE"

    UNKNOWN = "UNKNOWN"