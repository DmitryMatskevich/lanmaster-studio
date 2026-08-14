from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PINNED_REQUIREMENT = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[A-Za-z0-9_.!+-]+$")


def _python_dependencies() -> list[dict[str, str]]:
    deps = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        if not PINNED_REQUIREMENT.match(item):
            raise AssertionError(f"Python dependency is not exactly pinned: {item}")
        name, version = item.split("==", 1)
        deps.append({"ecosystem": "python", "name": name, "version": version})
    return deps


def _npm_dependencies() -> list[dict[str, str]]:
    lock_path = ROOT / "frontend" / "package-lock.json"
    if not lock_path.exists():
        raise AssertionError("frontend/package-lock.json is required for dependency policy")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock.get("packages", {})
    deps = []
    for path, data in sorted(packages.items()):
        if path == "" or "node_modules/" not in path:
            continue
        name = path.split("node_modules/", 1)[1]
        version = data.get("version")
        if not version:
            raise AssertionError(f"NPM dependency has no locked version: {name}")
        deps.append({"ecosystem": "npm", "name": name, "version": version})
    return deps


def build_sbom() -> dict[str, object]:
    components = _python_dependencies() + _npm_dependencies()
    return {
        "bomFormat": "LANMASTER-Studio-SBOM",
        "specVersion": "1",
        "componentCount": len(components),
        "components": components,
        "policy": {
            "pythonExactPinsRequired": True,
            "npmLockfileRequired": True,
            "frontendAuditCommand": "npm audit --prefix frontend --audit-level=moderate",
        },
    }


def main() -> None:
    out = ROOT / "docs" / "discovery" / "p7-04-sbom.json"
    sbom = build_sbom()
    out.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Security policy verification passed: {sbom['componentCount']} components")
    print(out)


if __name__ == "__main__":
    main()
