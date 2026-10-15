import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .config import FRONTEND_DIR
from .routes.conversion import router as conversion_router
from .routes.files import router as files_router
from .routes.merge import router as merge_router
from .storage import cleanup_expired_files


async def _cleanup_loop():
    while True:
        await asyncio.sleep(60 * 60)
        await asyncio.to_thread(cleanup_expired_files)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await asyncio.to_thread(cleanup_expired_files)
    task = asyncio.create_task(_cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

app = FastAPI(title="Paperplane PDF Toolkit", docs_url=None, redoc_url=None, lifespan=lifespan)
app.include_router(merge_router, prefix="/api")
app.include_router(conversion_router, prefix="/api")
app.include_router(files_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/{path:path}")
def frontend(path: str):
    root = FRONTEND_DIR.resolve()
    requested = (root / path).resolve()
    if not requested.is_relative_to(root):
        raise HTTPException(404)
    target = requested if requested.is_file() else root / "index.html"
    if not target.is_file():
        raise HTTPException(404)
    return FileResponse(target)
