from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = {
    "docs/guides/engineer.md": ["source", "PMD", "preview", "release", "pytest"],
    "docs/guides/librarian.md": ["provenance", "SHA-256", "source gaps", "component tables", "email"],
    "docs/guides/administrator.md": ["pinned images", "backups", "monitor", "rollback", "RAG"],
}


def main() -> None:
    for rel_path, terms in GUIDES.items():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        missing = [term for term in terms if term not in text]
        if missing:
            raise AssertionError(f"{rel_path} misses required guide terms: {', '.join(missing)}")
    print("Guide verification passed")


if __name__ == "__main__":
    main()

