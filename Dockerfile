FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install --no-audit --no-fund
COPY vite.config.js tailwind.config.js postcss.config.js tsconfig.json ./
COPY index.html ./
COPY src ./src
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=frontend-build /app/dist ./frontend
RUN useradd --create-home --uid 10001 appuser && mkdir /data && chown -R appuser:appuser /app /data
USER appuser
EXPOSE 8080
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
