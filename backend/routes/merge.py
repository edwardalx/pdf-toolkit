import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from ..config import MAX_MERGE_FILES
from ..services.pdf import merge_pdfs
from ..storage import save_generated_file, validate_workspace_id
from ..uploads import save_upload

router = APIRouter()


@router.post("/merge")
async def merge_endpoint(files: list[UploadFile] = File(...), workspace_id: str = Header(alias="X-Workspace-Id")):
    workspace_id = validate_workspace_id(workspace_id)
    if len(files) < 2:
        raise HTTPException(400, "Choose at least two PDFs to merge.")
    if len(files) > MAX_MERGE_FILES:
        raise HTTPException(400, f"Merge up to {MAX_MERGE_FILES} PDFs at a time.")

    folder = Path(tempfile.mkdtemp(prefix="paperplane-"))
    try:
        paths = [await save_upload(upload, folder, (".pdf",)) for upload in files]
        output = folder / "merged.pdf"
        try:
            merge_pdfs(paths, output)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        return save_generated_file(output, "merged.pdf", workspace_id)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
