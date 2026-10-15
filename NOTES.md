# Project notes

Keep evolving implementation decisions and development notes here. Put stable setup, usage, and deployment instructions in [README.md](README.md).

## Decisions

- Keep the existing Paperplane interface design while organizing the frontend into TypeScript React components styled with Tailwind.
- Keep FastAPI routes, file handling, configuration, and document conversion services in separate backend modules.
- Process incoming uploads in per-request temporary folders and remove them after processing.
- Retain generated files for seven days in server storage, outside the application source directory. In Docker Compose, use the persistent `paperplane_data` volume mounted at `/data`.
- Show generated files in the “Ready to download” section. The list is scoped to the browser workspace; clearing that browser's local storage removes its access to the list.
- Run the expiry cleanup hourly when the API is running, and once during API startup.
- Deploy the single Compose service to `eobkwaku@eobserver:/home/eobkwaku/pdf-converter` from Jenkins. The pipeline targets branch `trunk`, uses credential ID `pdf-toolkit-deploy-key`, requires a clean remote checkout, and preserves the generated-file volume.
- In production, serve the combined frontend/API behind a separate Nginx virtual host; Compose publishes the app only at `127.0.0.1:8080` by default.

## Operational follow-ups

- Keep the app on a trusted network or behind an authenticated reverse proxy; the app does not currently provide user accounts or authentication.
- Back up the Docker `paperplane_data` volume if retained outputs need disaster recovery.
- If running the backend outside Docker, configure `PAPERPLANE_STORAGE_DIR` to a persistent folder on the server.
