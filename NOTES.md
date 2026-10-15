# Project notes

Keep evolving implementation decisions and development notes here. Put stable setup, usage, and deployment instructions in [README.md](README.md).

## Decisions

- Keep the existing Paperplane interface design while organizing the frontend into TypeScript React components styled with Tailwind.
- Keep FastAPI routes, file handling, configuration, and document conversion services in separate backend modules.
- Process incoming uploads in per-request temporary folders and remove them after processing.
- Retain generated files for seven days in server storage, outside the application source directory. In Docker Compose, use the persistent `paperplane_data` volume mounted at `/data`.
- Show generated files in the “Ready to download” section. The list is scoped to the browser workspace; clearing that browser's local storage removes its access to the list.
- Run the expiry cleanup hourly when the API is running, and once during API startup.

## Operational follow-ups

- Keep the app on a trusted network or behind an authenticated reverse proxy; the app does not currently provide user accounts or authentication.
- Back up the Docker `paperplane_data` volume if retained outputs need disaster recovery.
- If running the backend outside Docker, configure `PAPERPLANE_STORAGE_DIR` to a persistent folder on the server.
