from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import HTTPException

from .config import FILE_RETENTION_DAYS, STORAGE_DIR


def validate_workspace_id(value: str) -> str:
    try:
        normalized = value.lower()
        if len(normalized) != 36 or str(uuid.UUID(normalized)) != normalized:
            raise ValueError
        return normalized
    except (ValueError, AttributeError):
        raise HTTPException(400, "A valid workspace ID is required.") from None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _metadata_path(file_id: str) -> Path:
    return STORAGE_DIR / f"{file_id}.json"


def _load_metadata(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_generated_file(source: Path, filename: str, workspace_id: str) -> dict:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    file_id = uuid.uuid4().hex
    now = _now()
    data_path = STORAGE_DIR / f"{file_id}{source.suffix.lower()}"
    metadata_path = _metadata_path(file_id)
    shutil.copyfile(source, data_path)
    metadata = {
        "id": file_id,
        "filename": Path(filename).name,
        "size": data_path.stat().st_size,
        "createdAt": now.isoformat(),
        "expiresAt": (now + timedelta(days=FILE_RETENTION_DAYS)).isoformat(),
        "workspaceId": workspace_id,
        "path": data_path.name,
    }
    try:
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    except Exception:
        data_path.unlink(missing_ok=True)
        raise
    return metadata


def list_files(workspace_id: str) -> list[dict]:
    if not STORAGE_DIR.exists():
        return []
    files = []
    for metadata_path in STORAGE_DIR.glob("*.json"):
        metadata = _load_metadata(metadata_path)
        if metadata and metadata.get("workspaceId") == workspace_id:
            files.append(metadata)
    return sorted(files, key=lambda item: item["createdAt"], reverse=True)


def get_file(file_id: str, workspace_id: str) -> tuple[Path, dict]:
    if len(file_id) != 32 or any(char not in "0123456789abcdef" for char in file_id):
        raise HTTPException(404, "File not found or expired.")
    metadata = _load_metadata(_metadata_path(file_id))
    if not metadata or metadata.get("workspaceId") != workspace_id:
        raise HTTPException(404, "File not found or expired.")
    path = STORAGE_DIR / metadata["path"]
    if not path.is_file():
        _metadata_path(file_id).unlink(missing_ok=True)
        raise HTTPException(404, "File not found or expired.")
    return path, metadata


def delete_file(file_id: str, workspace_id: str) -> None:
    path, _ = get_file(file_id, workspace_id)
    path.unlink(missing_ok=True)
    _metadata_path(file_id).unlink(missing_ok=True)


def cleanup_expired_files() -> int:
    if not STORAGE_DIR.exists():
        return 0
    now = _now()
    deleted = 0
    for metadata_path in STORAGE_DIR.glob("*.json"):
        metadata = _load_metadata(metadata_path)
        if not metadata:
            continue
        try:
            expired = datetime.fromisoformat(metadata["expiresAt"]) <= now
        except (KeyError, TypeError, ValueError):
            expired = True
        if expired:
            if isinstance(metadata.get("path"), str):
                (STORAGE_DIR / Path(metadata["path"]).name).unlink(missing_ok=True)
            metadata_path.unlink(missing_ok=True)
            deleted += 1
    return deleted
