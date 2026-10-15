from __future__ import annotations

import subprocess
from pathlib import Path


def convert_docx_to_pdf(source: Path, output: Path, profile: Path) -> None:
    command = [
        "soffice",
        f"-env:UserInstallation=file://{profile}",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(source.parent),
        str(source),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError("LibreOffice is not available on this server.") from exc
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError("Word to PDF conversion timed out after two minutes.") from exc

    converted = source.with_suffix(".pdf")
    if result.returncode != 0 or not converted.exists():
        detail = (result.stderr or result.stdout or "LibreOffice could not open this document.").strip()[-700:]
        raise ValueError(f"Word to PDF conversion failed: {detail}")
    converted.replace(output)
