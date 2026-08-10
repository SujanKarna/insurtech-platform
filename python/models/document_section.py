from dataclasses import dataclass, field

from models.document_zone import DocumentZone
from models.raw_page import RawPage
from models.section import Section


@dataclass
class DocumentSection:

    zone: DocumentZone

    pages: list[RawPage] = field(
        default_factory=list
    )

    sections: list[Section] = field(
        default_factory=list
    )

    @property
    def start_page(self) -> int:
        return self.pages[0].page_number

    @property
    def end_page(self) -> int:
        return self.pages[-1].page_number

    @property
    def page_count(self) -> int:
        return len(self.pages)