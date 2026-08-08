from config.settings import (
    GDV_AUB_RAW_PATH,
    GDV_AUB_URL,
)
from etl.extract.downloader import download_document


def run_pipeline() -> None:
    print("Starting insurance document pipeline...")

    # -----------------------------------------------------------------------
    # Extract
    # -----------------------------------------------------------------------

    print("Downloading GDV AUB document...")

    document = download_document(
        url=GDV_AUB_URL,
        destination=GDV_AUB_RAW_PATH,
    )

    print(f"Document: {document.file_name}")
    print(f"Location: {document.file_path}")
    print(f"Size: {document.file_size} bytes")
    print(f"SHA-256: {document.sha256}")
    print(f"Downloaded At: {document.downloaded_at}")

    print("Pipeline finished.")


if __name__ == "__main__":
    run_pipeline()