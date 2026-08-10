from models.document_section import DocumentSection
from models.document_zone import DocumentZone
from models.raw_document import RawDocument

from etl.transform.zone_detector import detect_zones


def extract_zone(
    document: RawDocument,
    zone: DocumentZone,
) -> DocumentSection:
    """
    Extract a logical document zone from a RawDocument.

    The returned DocumentSection contains the original
    RawPage objects. No text or metadata is modified.
    """

    zones = detect_zones(document)

    for zone_range in zones:

        if zone_range.zone != zone:
            continue

        pages = [
            page
            for page in document.pages
            if (
                zone_range.start_page
                <= page.page_number
                <= zone_range.end_page
            )
        ]

        if not pages:
            raise ValueError(
                f"Zone '{zone.value}' was detected, "
                "but no pages were found."
            )

        return DocumentSection(
            zone=zone,
            pages=pages,
        )

    raise ValueError(
        f"Zone '{zone.value}' was not found "
        "in the document."
    )