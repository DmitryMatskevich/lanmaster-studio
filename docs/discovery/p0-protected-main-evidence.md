# P0 Protected Main Evidence

Status: external blocker.

Evidence date: 2026-08-13.

## Local Evidence

| Check | Evidence | Result |
|---|---|---|
| Current branch | `git branch --show-current` -> `main` | pass |
| CI skeleton targets main | `.github/workflows/ci.yml` runs on `push` and `pull_request` to `main` | pass |
| CI executes verifier | `.github/workflows/ci.yml` runs `python3 scripts/verify_skeleton.py` | pass |
| Ownership metadata exists | `.github/CODEOWNERS` defines default owner `@lanmaster-studio/tech-leads` | pass |

## External Evidence

`git remote -v` produced no configured remote for `lanmaster-studio`, so GitHub
branch-protection settings cannot be inspected from the local repository.

Gate P0 cannot claim protected `main` until one of these is recorded:

- GitHub branch protection/API evidence showing required pull request review and
  required CI status checks for `main`; or
- an explicit project-owner decision that P0 accepts local CI/CODEOWNERS evidence
  before remote repository creation.
