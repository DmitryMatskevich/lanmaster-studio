# P4-06 Object Storage And Signed URLs Evidence

Status: passed.

Date: 2026-08-14.

## Scope

P4-06 adds a local object-storage adapter for the developer stack:

- upload intent with expected filename, media type, size, SHA-256 and scope;
- local `file://` upload target under configured storage root;
- complete-upload verifies object existence, byte size and SHA-256;
- artifact metadata persists as pending/ready;
- signed download URL with expiry and HMAC signature;
- actual download endpoint verifies signature and returns file content;
- OpenAPI and TypeScript client include artifact methods.

This is intentionally a local adapter. Production S3/MinIO lifecycle remains a
deployment decision, but the API contract is now stable enough for P4/P5 work.

## Implemented Endpoints

- `POST /api/v1/documents/upload-intents`
- `POST /api/v1/documents/complete-upload`
- `GET /api/v1/artifacts/{artifact_id}`
- `GET /api/v1/artifacts/{artifact_id}/download-url`
- `GET /api/v1/artifacts/{artifact_id}/download`

## Verification

Commands:

```bash
.venv/bin/python scripts/generate_openapi.py
.venv/bin/python scripts/generate_ts_client.py
.venv/bin/python -m pytest
DATABASE_URL=sqlite:///./var/p4-06-web-check-2.db STUDIO_STORAGE_DIR=./var/p4-06-storage-2 .venv/bin/uvicorn studio_api.main:app --host 127.0.0.1 --port 8093
# HTTP smoke: upload intent -> write file -> complete upload -> signed URL -> download bytes
```

Results:

- `pytest`: 9 passed.
- upload intent returned `file://.../download.txt`.
- complete-upload returned ready artifact with expected SHA-256.
- signed URL returned `/api/v1/artifacts/.../download?...signature=...`.
- download endpoint returned original bytes.
- Swagger UI `/docs` loaded and referenced `/api/v1/openapi.json`.

## Next

P4-07: WebSocket events and REST replay.

