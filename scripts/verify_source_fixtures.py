#!/usr/bin/env python3
"""Verify controlled source-format fixtures for P0/P3 intake smoke."""

from __future__ import annotations

import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "test-fixtures" / "source-formats"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(name: str) -> Path:
    path = FIXTURES / name
    if not path.is_file():
        fail(f"missing fixture: {name}")
    if path.stat().st_size <= 0:
        fail(f"empty fixture: {name}")
    return path


def verify_svg() -> None:
    root = ET.parse(require_file("minimal-panel.svg")).getroot()
    if not root.tag.endswith("svg"):
        fail("minimal-panel.svg root is not SVG")
    if not root.findall(".//{http://www.w3.org/2000/svg}rect"):
        fail("minimal-panel.svg missing rectangle geometry")


def verify_dxf() -> None:
    import ezdxf

    doc = ezdxf.readfile(require_file("minimal-panel.dxf"))
    entities = list(doc.modelspace())
    if len(entities) < 2:
        fail("minimal-panel.dxf has too few modelspace entities")


def verify_dwg() -> None:
    result = subprocess.run(
        ["dwgread", str(require_file("minimal-panel.dwg"))],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    combined = result.stdout + result.stderr
    if result.returncode != 0 or "SUCCESS" not in combined:
        fail(f"dwgread failed for minimal-panel.dwg: {combined[:400]}")


def verify_step() -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(require_file("frwaj-open-frame.step")))
    if status != IFSelect_RetDone:
        fail(f"STEP reader returned {status!r}")


def verify_manifest() -> None:
    text = require_file("manifest.yml").read_text(encoding="utf-8")
    for phrase in (
        "Controlled parser fixtures",
        "not official product evidence",
        "minimal-panel.dwg",
        "frwaj-open-frame.step",
    ):
        if phrase not in text:
            fail(f"fixture manifest missing: {phrase}")


def main() -> None:
    verify_manifest()
    verify_svg()
    verify_dxf()
    verify_dwg()
    verify_step()
    print("Source fixture verification passed")


if __name__ == "__main__":
    main()
