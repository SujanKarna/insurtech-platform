from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen

from config.settings import (
    DOWNLOAD_CHUNK_SIZE_BYTES,
    DOWNLOAD_TIMEOUT_SECONDS,
)
from models.provenance import DocumentProvenance


def download_document(
    url: str,
    destination: Path,
) -> DocumentProvenance:
    """
    Download a document and create its provenance metadata.

    The document is downloaded in chunks while its SHA-256 hash
    is calculated at the same time.
    """

    destination = Path(destination)

    # -----------------------------------------------------------------------
    # Create destination directory
    # -----------------------------------------------------------------------

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------------------------
    # If the file already exists, don't download it again.
    # Recalculate its hash and create/update provenance.
    # -----------------------------------------------------------------------

    if destination.exists():

        file_size = destination.stat().st_size
        file_hash = calculate_sha256(destination)

        provenance = DocumentProvenance(
            source_url=url,
            file_name=destination.name,
            file_path=destination,
            file_size=file_size,
            sha256=file_hash,
            downloaded_at=datetime.now(timezone.utc),
        )

        save_provenance(
            destination=destination,
            provenance=provenance,
        )

        return provenance

    # -----------------------------------------------------------------------
    # Create HTTP request
    # -----------------------------------------------------------------------

    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
    )

    # -----------------------------------------------------------------------
    # Download and calculate SHA-256 simultaneously
    # -----------------------------------------------------------------------

    file_hash = sha256()
    file_size = 0

    with urlopen(
        request,
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
    ) as response:

        with destination.open("wb") as file:

            while chunk := response.read(
                DOWNLOAD_CHUNK_SIZE_BYTES
            ):
                file.write(chunk)

                file_hash.update(chunk)

                file_size += len(chunk)

    # -----------------------------------------------------------------------
    # Create provenance
    # -----------------------------------------------------------------------

    provenance = DocumentProvenance(
        source_url=url,
        file_name=destination.name,
        file_path=destination,
        file_size=file_size,
        sha256=file_hash.hexdigest(),
        downloaded_at=datetime.now(timezone.utc),
    )

    # -----------------------------------------------------------------------
    # Save provenance beside the document
    # -----------------------------------------------------------------------

    save_provenance(
        destination=destination,
        provenance=provenance,
    )

    return provenance


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate the SHA-256 hash of an existing file.
    """

    file_hash = sha256()

    with file_path.open("rb") as file:

        while chunk := file.read(
            DOWNLOAD_CHUNK_SIZE_BYTES
        ):
            file_hash.update(chunk)

    return file_hash.hexdigest()


def save_provenance(
    destination: Path,
    provenance: DocumentProvenance,
) -> None:
    """
    Save provenance as a JSON sidecar file next to the downloaded document.
    """

    provenance_path = destination.with_suffix(".json")

    provenance.save(provenance_path)