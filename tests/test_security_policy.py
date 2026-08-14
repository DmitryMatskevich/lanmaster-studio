from __future__ import annotations

from scripts.verify_security_policy import build_sbom


def test_security_policy_builds_sbom_with_python_and_npm_components():
    sbom = build_sbom()

    ecosystems = {component["ecosystem"] for component in sbom["components"]}
    assert {"python", "npm"}.issubset(ecosystems)
    assert sbom["componentCount"] == len(sbom["components"])
    assert sbom["policy"]["pythonExactPinsRequired"] is True
    assert sbom["policy"]["npmLockfileRequired"] is True

