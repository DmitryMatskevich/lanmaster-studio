FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/var/studio.db \
    STUDIO_STORAGE_DIR=/app/var/storage \
    STUDIO_ENV=dev \
    STUDIO_AUTH_MODE=dev

WORKDIR /app

RUN adduser --disabled-password --gecos "" studio

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY studio_api ./studio_api
COPY migrations ./migrations
COPY scripts ./scripts
COPY openapi ./openapi
COPY clients ./clients
COPY README.md STATUS.md ./

RUN mkdir -p /app/var/storage \
    && chown -R studio:studio /app

USER studio

EXPOSE 8088

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/health', timeout=3).read()"

CMD ["uvicorn", "studio_api.main:app", "--host", "0.0.0.0", "--port", "8088"]
