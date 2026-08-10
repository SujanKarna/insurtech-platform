from dataclasses import dataclass

from models.document_zone import DocumentZone


@dataclass
class DocumentZoneRange:

    zone: DocumentZone

    start_page: int
    end_page: int

    @property
    def page_count(self)-> int:
        return self.end_page - self.start_page + 1