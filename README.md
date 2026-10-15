# Paperplane PDF Toolkit

A self-hosted React app for merging PDF files, converting PDF to Word, and converting Word documents to PDF. Uploads are processed on the server. Generated files are saved in server storage for seven days and can be downloaded from the app's “Ready to download” list. No third-party conversion service is used.

## Run with Docker Compose

Install Docker Engine with the Compose plugin (or Docker Desktop), then from this directory:

```sh
docker compose up -d --build
```

For local use, open `http://localhost:8081`. Compose binds the app to `127.0.0.1:8081` by default so production traffic can go through Nginx without colliding with services already using port 8080. Set another loopback port by creating a `.env` file with `PORT=8090` before starting Compose.

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

## Deploy to the on-prem server with Jenkins

The app is built as one Docker Compose service: FastAPI serves the compiled React frontend as well as the API. Nginx should proxy the whole hostname to the app; the FE and API share one origin. Generated files remain in the named `paperplane_data` volume across deployments. The checked-in [Jenkinsfile](Jenkinsfile) deploys branch `trunk` to `eobkwaku@eobserver:/home/eobkwaku/pdf-converter`.

The production FE URL is `https://pdf-gh.giize.com/`; the API is under the same origin at `/api`. The public ports 80 and 443 are owned by the existing `campushostels_nginx` Docker container, so configure that container's mounted Nginx directory at `/home/eobkwaku/jenkins-docker/CampusHostels/nginx/conf.d`, not the host's `/etc/nginx/sites-available`.

The production overlay [compose.production.yaml](compose.production.yaml) attaches Paperplane to the existing `campushostels_campushostels_net` Docker network. Jenkins deploys with this overlay; the normal `compose.yaml` remains suitable for local development. The Nginx templates proxy to `http://paperplane:8080` over that shared network. Keep the Let's Encrypt certificate for `pdf-gh.giize.com` available in the existing `/etc/letsencrypt` mount. This server issues/renews it using the configured Dynu DNS hooks.

After committing and pushing changes to `trunk`, run the Jenkins deployment so Paperplane joins the shared network. Then install the HTTPS virtual host into the mounted Nginx config directory and reload the container:

```sh
cp /home/eobkwaku/pdf-converter/deploy/nginx-paperplane.conf.example /home/eobkwaku/jenkins-docker/CampusHostels/nginx/conf.d/pdf-gh.conf
docker exec campushostels_nginx nginx -t
docker exec campushostels_nginx nginx -s reload
```

The template allows up to 2 GB request bodies for the app's configured 20-file merge limit at 100 MB per file. DNS for `pdf-gh.giize.com` must point to this server and inbound ports 80 and 443 must be allowed. Preserve the other virtual hosts in the shared Nginx config directory.

### Prepare the server once

1. Install Docker Engine and the Docker Compose plugin on `eobserver`. Give `eobkwaku` permission to run Docker, then start a fresh login session and confirm `docker compose version` works.
2. Make sure the server can fetch the app's Git repository. For a private repository, configure a read-only deploy key for the `eobkwaku` account.
3. Clone the repository into the deployment directory, replacing `<GIT_REPOSITORY_URL>` with its SSH or HTTPS Git URL:

   ```sh
   git clone --branch trunk <GIT_REPOSITORY_URL> /home/eobkwaku/pdf-converter
   ```

4. Confirm the checkout is clean, its current branch is `trunk`, and `git remote -v` shows `origin`. The Compose app uses a Docker-managed volume for retained files; it does not need the Windows `local.env` file.

### Configure Jenkins

1. Ensure the Jenkins agent can resolve and SSH to `eobserver`. Add the server's verified host key to the Jenkins agent's `known_hosts`; keep host-key checking enabled.
2. In **Manage Jenkins → Credentials**, add an **SSH Username with private key** credential with ID `pdf-toolkit-deploy-key` and username `eobkwaku`. The key must allow Jenkins to SSH to the server. The server separately needs Git access as described above.
3. Create a Pipeline job using **Pipeline script from SCM**. Select Git, enter the same repository URL and any required SCM credentials, set the branch to `*/trunk`, and set the script path to `Jenkinsfile`.
4. Run the job. It checks that the server checkout has no uncommitted changes and is on `trunk`, fetches and fast-forward pulls the branch, runs `docker compose up -d --build --remove-orphans`, then checks `/api/health` inside the app container.

The pipeline defaults are at the top of `Jenkinsfile`. If the Git default branch or server address changes, update `DEPLOY_BRANCH` or `DEPLOY_HOST` there and keep the README instructions aligned. The current working copy has no Git remote configured, so supply the actual repository URL when setting up Jenkins and cloning on the server. A failed health check prints the recent Compose logs and fails the Jenkins build; the pipeline does not stash or discard server-side edits.

For evolving project decisions and development notes, see [NOTES.md](NOTES.md).

## Network access

The Compose file exposes the app only on host loopback; Nginx provides the public HTTPS endpoint. The app does not include authentication, so keep the hostname on a trusted network or add authentication at the reverse proxy before exposing it publicly.
