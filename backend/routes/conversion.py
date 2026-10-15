import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from ..services.office import convert_docx_to_pdf
from ..services.pdf import convert_pdf_to_docx
from ..storage import save_generated_file, validate_workspace_id
from ..uploads import safe_stem, save_upload

router = APIRouter()


@router.post("/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...), mode: str = Form("editable"), workspace_id: str = Header(alias="X-Workspace-Id")):
    workspace_id = validate_workspace_id(workspace_id)
    if mode not in {"editable", "exact", "hybrid"}:
        raise HTTPException(400, "Choose editable, exact, or hybrid conversion.")
    folder = Path(tempfile.mkdtemp(prefix="paperplane-"))
    try:
        source = await save_upload(file, folder, (".pdf",))
        output = folder / f"{safe_stem(file.filename or 'document')}_{mode}.docx"
        try:
            convert_pdf_to_docx(source, output, mode)
        except Exception as exc:
            raise HTTPException(400, f"Could not convert this PDF: {exc}") from exc
        return save_generated_file(output, output.name, workspace_id)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise


@router.post("/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...), workspace_id: str = Header(alias="X-Workspace-Id")):
    workspace_id = validate_workspace_id(workspace_id)
    folder = Path(tempfile.mkdtemp(prefix="paperplane-"))
    try:
        source = await save_upload(file, folder, (".docx",))
        output = folder / f"{safe_stem(file.filename or 'document')}.pdf"
        try:
            convert_docx_to_pdf(source, output, folder / "lo-profile")
        except FileNotFoundError as exc:
            raise HTTPException(503, "LibreOffice is not available on this server.") from exc
        except TimeoutError as exc:
            raise HTTPException(504, str(exc)) from exc
        except Exception as exc:
            raise HTTPException(400, str(exc)) from exc
        return save_generated_file(output, f"{source.stem}.pdf", workspace_id)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
