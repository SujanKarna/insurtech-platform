from enum import Enum


class SectionType(str, Enum):
    PART = "PART"
    SECTION = "SECTION"
    SUBSECTION = "SUBSECTION"
    UNKNOWN = "UNKNOWN"