from pathlib import Path



# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"


# ---------------------------------------------------------------------------
# Source documents
# ---------------------------------------------------------------------------

GDV_AUB_URL = "https://www.gdv.de/resource/blob/6252/6fde83896927a4920772d713456a646d/01-allgemeine-unfallversicherungsbedingungen-aub-2020--data.pdf"

GDV_AUB_FILENAME = "gdv_aub.pdf"

GDV_AUB_RAW_PATH = RAW_DATA_DIR / "gdv" / "aub" / GDV_AUB_FILENAME


# ---------------------------------------------------------------------------
# Download configuration
# ---------------------------------------------------------------------------

DOWNLOAD_TIMEOUT_SECONDS = 60
DOWNLOAD_CHUNK_SIZE_BYTES = 8192

# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

BODY_TEXT_FONT_SIZE = 9.96
FONT_SIZE_TOLERANCE = 0.05



# ---------------------------------------------------------------------------
# Processed document artifacts
# ---------------------------------------------------------------------------

CHUNKS_DIR = PROCESSED_DATA_DIR / "chunks"

GDV_AUB_CHUNKS_PATH = (
    CHUNKS_DIR / "gdv_aub_chunks.jsonl"
)


# ---------------------------------------------------------------------------
# Embedding configuration
# ---------------------------------------------------------------------------

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

EMBEDDING_DIMENSION = 1024

EMBEDDINGS_DIR = (
    PROCESSED_DATA_DIR
    / "embeddings"
)

GDV_AUB_EMBEDDINGS_PATH = (
    EMBEDDINGS_DIR
    / "gdv_aub_embeddings.jsonl"
)



# ============================================================
# QDRANT
# ============================================================

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

QDRANT_COLLECTION_NAME = "gdv_aub"

QDRANT_VECTOR_SIZE = 1024
QDRANT_DISTANCE = "Cosine"