# Defines the structure of provenance of the document as a whole
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DocumentProvenance:

    source_url: str
    file_path: Path
    file_name: str
    file_size: int
    sha256: str
    downloaded_at: datetime


    def to_dict(self)-> dict:

        return {
            "source_url": self.source_url,
            "file_name": self.file_name,
            "file_path": str(self.file_path),
            "file_size": self.file_size,
            "sha256": self.sha256,
            "downloaded_at": self.downloaded_at.isoformat(),
        }

    def save(self, path: Path) -> None:
        """
        Save provenance information as a JSON sidecar file.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )