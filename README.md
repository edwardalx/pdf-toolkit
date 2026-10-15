# Paperplane PDF Toolkit

A self-hosted React app for merging PDF files, converting PDF to Word, and converting Word documents to PDF. Uploads are processed on the server. Generated files are saved in server storage for seven days and can be downloaded from the app's “Ready to download” list. No third-party conversion service is used.

## Run with Docker Compose

Install Docker Engine with the Compose plugin (or Docker Desktop), then from this directory:

```sh
docker compose up -d --build
```

Open `http://localhost:8080`. On a local server, use `http://SERVER-IP:8080` from your LAN. Set another host port by creating a `.env` file with `PORT=8090` before starting Compose.

Stop the app with `docker compose down`. The service restarts automatically after a host reboot, and Docker health checks the API.

## Features

- Merge 2–20 PDF files, with ordering controls.
- Convert PDF to Word in editable text, appearance-preserving, or hybrid mode.
- Convert DOCX to PDF with LibreOffice bundled in the container.
- Keep generated files available to the originating browser for seven days.
- Automatically remove expired generated files every hour.

Editable PDF conversion works best for PDFs with selectable text. Scanned documents require OCR and will not produce editable text in the current version. Word-to-PDF accepts `.docx` files.

## Development

Install the frontend dependencies with `npm install`, then start Vite with `npm run dev` at `http://localhost:5173`. The Vite development server proxies `/api` requests to `http://localhost:8080`.

For the backend on Windows, install its dependencies and start the server from the project root:

```powershell
cd C:\Users\obedd\MyAlxProjects\pdf-toolkit
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app:app --reload --port 8080
```

The backend automatically reads `local.env` at startup. Set `PAPERPLANE_STORAGE_DIR` there to choose where generated files are retained; this local file is ignored by Git. This Windows checkout uses `%LOCALAPPDATA%/PaperplaneData`, which expands to a folder under your Windows user profile. On another machine, create `local.env` in the project root with:

```env
PAPERPLANE_STORAGE_DIR=%LOCALAPPDATA%/PaperplaneData
```

Run `npm run build` to type-check the TypeScript app and create the production bundle.

The frontend entry points are `src/main.tsx` and `src/App.tsx`. Reusable UI lives in `src/components`, and file handling helpers live in `src/utils`. The FastAPI app is assembled in `backend/app.py`; route handlers, upload and storage helpers, configuration, and document conversion services are separated into their own modules. If `PAPERPLANE_STORAGE_DIR` is unset, local development uses the operating system's temporary directory under `paperplane-storage`.

Docker Compose stores generated files in the persistent `paperplane_data` volume mounted at `/data`, separate from the application directory. The volume survives container restarts and rebuilds. The saved-file list is tied to the browser that created the files; clearing that browser's local storage loses its list access. The app does not currently include user accounts or authentication, so keep it on a trusted network or behind an authenticated reverse proxy.

For evolving project decisions and development notes, see [NOTES.md](NOTES.md).

## Network access

The Compose file publishes the app on all host interfaces so it can be used from a local network. It does not include authentication or TLS. Keep it on a trusted LAN, or put it behind an authenticated HTTPS reverse proxy before exposing it beyond your network.
