# Engineer Guide

## Purpose

Use Studio to review sources, inspect PMD revisions, run previews, accept RAG
patch proposals and prepare release candidates.

## Required Workflow

1. Confirm source artifacts are immutable and have SHA-256 provenance.
2. Review PMD component tree, parameters and generated views before commit.
3. Use preview jobs for draft changes; do not publish preview artifacts.
4. Accept only patch proposals with cited source evidence.
5. Run release only from an immutable revision after quality gates pass.
6. Keep known defects scoped to baseline evidence; do not weaken release gates.

## Verification Commands

```bash
.venv/bin/python -m pytest
npm run frontend:build
PYTHON=.venv/bin/python npm --prefix frontend run test:e2e
```

