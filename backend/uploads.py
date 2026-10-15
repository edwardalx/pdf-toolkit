from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from .config import MAX_FILE_BYTES


def safe_stem(filename: str) -> str:
    stem = Path(filename).stem
    return re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._") or "document"


async def save_upload(upload: UploadFile, folder: Path, extensions: tuple[str, ...]) -> Path:
    name = upload.filename or ""
    if not name.lower().endswith(extensions):
        raise HTTPException(400, f"Unsupported file type: {name or 'unnamed file'}")
    target = folder / f"{uuid.uuid4().hex}{Path(name).suffix.lower()}"
    size = 0
    with target.open("wb") as output:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                target.unlink(missing_ok=True)
                raise HTTPException(413, "Each file must be smaller than 100 MB.")
            output.write(chunk)
    if size == 0:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "The uploaded file is empty.")
    return target
