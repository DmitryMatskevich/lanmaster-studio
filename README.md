# LANMASTER Studio

Separate web application and orchestration workspace for LANMASTER Studio.

This repository owns the Studio application layer: web UI, API, workers orchestration,
audit, revision management, and future RAG/chat workflows. CAD geometry, PMD core,
compiler, geometry backends, exporters, and legacy compatibility remain in the
separate `lanmaster-cad` repository until their roadmap tasks explicitly require
changes there.

## Current Scope

Active roadmap checkpoint: P3-01 from `plan/lanmaster-studio/06-delivery-roadmap.md`.

The initial repository contains:

- CI skeleton for local and GitHub validation.
- Issue templates and labels for roadmap tracking.
- ADR directory for architecture decisions owned by Studio.
- `STATUS.md` as the compact continuation log for Codex work.

API, frontend, editor, and RAG implementation are intentionally absent until gates
P1, P2, and P3 are complete.

## Local Verification

```bash
python3 scripts/verify_skeleton.py
```

## External Repository Setup

After creating the remote repository, configure:

- protected `main` branch;
- required CI status checks;
- CODEOWNERS review requirement;
- issue labels from `.github/labels.yml`.
