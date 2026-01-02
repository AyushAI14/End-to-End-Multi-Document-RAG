from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Iterable, List

from multi_doc_chat.logger.customLogger import CustomLogger
from multi_doc_chat.exception.customException import DocumentPortalException

# Allowed file types
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".pptx", ".md",
    ".csv", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3"
}

log = CustomLogger().get_logger(__name__)


def save_uploaded_files(uploaded_files: Iterable, target_dir: Path) -> List[Path]:
    """
    Save uploaded files to disk and return their local paths.

    Supports:
    - FastAPI / Starlette UploadFile
    - Streamlit UploadedFile
    - Generic file-like objects
    """
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        saved_files: List[Path] = []

        for uf in uploaded_files:
            # Resolve original filename
            name = getattr(uf, "filename", getattr(uf, "name", "file"))
            ext = Path(name).suffix.lower()

            # Skip unsupported files
            if ext not in SUPPORTED_EXTENSIONS:
                log.warning("Unsupported file skipped", filename=name)
                continue

            # Sanitize name and generate unique filename
            safe_stem = re.sub(r"[^a-zA-Z0-9_-]", "_", Path(name).stem).lower()
            unique_name = f"{safe_stem}_{uuid.uuid4().hex[:8]}{ext}"
            output_path = target_dir / unique_name

            # Write file to disk
            with open(output_path, "wb") as f:
                # FastAPI / Starlette UploadFile
                if hasattr(uf, "file") and hasattr(uf.file, "read"):
                    f.write(uf.file.read())

                # Generic file-like object
                elif hasattr(uf, "read"):
                    data = uf.read()
                    if isinstance(data, memoryview):
                        data = data.tobytes()
                    f.write(data)

                # BytesIO / buffer-based object
                elif hasattr(uf, "getbuffer"):
                    data = uf.getbuffer()
                    if isinstance(data, memoryview):
                        data = data.tobytes()
                    f.write(data)

                else:
                    raise ValueError("Unsupported uploaded file object")

            saved_files.append(output_path)
            log.info(
                "File saved successfully",
                original_filename=name,
                saved_as=str(output_path),
            )

        return saved_files

    except Exception as e:
        log.error(
            "Failed to save uploaded files",
            error=str(e),
            target_dir=str(target_dir),
        )
        raise DocumentPortalException("Failed to save uploaded files", e) from e