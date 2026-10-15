from fastapi import APIRouter, Header, Response
from fastapi.responses import FileResponse
from mimetypes import guess_type

from ..storage import delete_file, get_file, list_files, validate_workspace_id

router = APIRouter()


@router.get("/files")
def ready_files(workspace_id: str = Header(alias="X-Workspace-Id")):
    return {"files": list_files(validate_workspace_id(workspace_id))}


@router.get("/files/{file_id}")
def download_file(file_id: str, workspace_id: str = Header(alias="X-Workspace-Id")):
    path, metadata = get_file(file_id, validate_workspace_id(workspace_id))
    return FileResponse(path, filename=metadata["filename"], media_type=guess_type(metadata["filename"])[0])


@router.delete("/files/{file_id}", status_code=204)
def remove_file(file_id: str, workspace_id: str = Header(alias="X-Workspace-Id")):
    delete_file(file_id, validate_workspace_id(workspace_id))
    return Response(status_code=204)
