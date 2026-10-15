---
name: paperplane-maintainer
description: Maintain and deploy the Paperplane PDF Toolkit. Use for changes to its React/TypeScript/Tailwind frontend, FastAPI backend, PDF/Word workflows, retained-file storage, Docker Compose, Jenkins deployment, or project documentation.
---

# Paperplane maintainer

Use this skill for work in this repository. Read [README.md](../../../README.md) for run and deployment steps and [NOTES.md](../../../NOTES.md) for current product decisions.

## Project structure and conventions

- Keep the existing Paperplane layout and visual design unless the user requests a redesign.
- The frontend uses React, strict TypeScript, Vite, and Tailwind. Keep the entry points as `src/main.tsx` and `src/App.tsx`; put reusable UI under `src/components` and shared browser helpers under `src/utils`. Prefer Tailwind utility classes; keep global CSS for resets and page-level defaults.
- The backend uses FastAPI. Keep route handlers in `backend/routes`, document processing in `backend/services`, and storage/configuration/upload concerns in their dedicated modules. Keep `backend/app.py` focused on application assembly and lifecycle.
- Preserve the JSON API contract and send the browser workspace ID (`X-Workspace-Id`) on file creation, listing, download, and delete requests.
- Keep `local.env` machine-specific and ignored by Git. Do not commit personal storage paths or secrets.

## File handling and retention

- Incoming uploads belong in per-request temporary folders and must be removed after processing.
- Generated downloads use the storage module and are retained for seven days. Keep them outside the application checkout: Docker Compose mounts the persistent `paperplane_data` volume at `/data`; Windows development reads `PAPERPLANE_STORAGE_DIR` from `local.env`.
- Preserve browser workspace ownership checks. Never return another workspace's files from list, download, or delete endpoints. The current app has no login system, so do not describe workspace IDs as account authentication.
- Preserve automatic expiry cleanup on startup and during operation. Do not remove, rename, or recreate the persistent volume as part of routine deployment.

## Deployment

- `Jenkinsfile` deploys branch `trunk` to `eobkwaku@eobserver:/home/eobkwaku/pdf-converter` using the Jenkins SSH credential ID `pdf-toolkit-deploy-key`.
- The target server checkout must have a clean working tree, be on the configured deployment branch, and have an `origin` remote. The pipeline uses a fast-forward-only pull and aborts on local edits; do not replace this with `git stash`, `git reset --hard`, or `docker compose down`.
- Keep SSH host-key checking enabled. Do not add credentials, private keys, or `StrictHostKeyChecking=no` to the pipeline.
- Deployment rebuilds the single Compose service, which serves both the API and built frontend. It waits for `/api/health` from inside the service. Keep generated files in the named Docker volume across deployments.
- Production Nginx should use a dedicated virtual host for Paperplane and proxy the entire origin (frontend and `/api`) to `127.0.0.1:8081`. Compose binds the app's container port 8080 to loopback host port 8081 by default; keep the separate Bookshelf virtual host untouched.
- Do not run the production Jenkins deployment unless the user explicitly asks. Prepare and review the configuration and instructions first.

## Documentation and verification

- Put stable setup and operations instructions in `README.md`; record evolving product/architecture decisions in `NOTES.md`.
- Keep deployment documentation in sync with `Jenkinsfile`, `compose.yaml`, and the configured branch, credential ID, host, and path.
- For frontend changes, run `npm run build` to type-check and build. For Python syntax checks, use `python -m compileall -q backend`. Do not add or run a test suite unless the user asks for tests or verification.
