import os
import tempfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def _load_local_environment(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


_load_local_environment(PROJECT_DIR / "local.env")

MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_MERGE_FILES = 20
FRONTEND_DIR = PROJECT_DIR / "frontend"
storage_dir = os.environ.get("PAPERPLANE_STORAGE_DIR", str(Path(tempfile.gettempdir()) / "paperplane-storage"))
STORAGE_DIR = Path(os.path.expandvars(storage_dir)).expanduser()
FILE_RETENTION_DAYS = 7
