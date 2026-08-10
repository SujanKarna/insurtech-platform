from dataclasses import dataclass, field

from models.provenance import DocumentProvenance
from models.raw_page import RawPage


@dataclass
class RawDocument:
    """
    Represents the raw extracted representation of a PDF document.
    """

    provenance: DocumentProvenance

    pages: list[RawPage] = field(
        default_factory=list
    )