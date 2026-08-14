from __future__ import annotations

import hashlib
import hmac
import time
from pathlib import Path
from urllib.parse import urlencode

from .config import Settings, get_settings


def storage_root(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    root = Path(settings.storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def object_path(object_key: str, settings: Settings | None = None) -> Path:
    root = storage_root(settings)
    path = (root / object_key).resolve()
    if not str(path).startswith(str(root.resolve())):
        raise ValueError("Invalid object key")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_file(path: Path) -> str:
    signatures = (b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE", b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$")
    with path.open("rb") as handle:
        sample = handle.read(1024 * 1024)
    if any(signature in sample for signature in signatures):
        return "malware_signature"
    return "clean"


def sign_download_path(artifact_id: str, object_key: str, ttl_seconds: int = 900) -> tuple[str, int]:
    expires = int(time.time()) + ttl_seconds
    secret = "lanmaster-studio-dev-signing-key"
    message = f"{artifact_id}:{object_key}:{expires}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    query = urlencode({"artifactId": artifact_id, "expires": expires, "signature": signature})
    return f"/api/v1/artifacts/{artifact_id}/download?{query}", expires


def verify_download_signature(artifact_id: str, object_key: str, expires: int, signature: str) -> bool:
    if expires < int(time.time()):
        return False
    secret = "lanmaster-studio-dev-signing-key"
    message = f"{artifact_id}:{object_key}:{expires}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
