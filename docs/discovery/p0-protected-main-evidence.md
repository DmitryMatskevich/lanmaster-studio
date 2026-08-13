# P0 Protected Main Evidence

Status: protected main configured.

Evidence date: 2026-08-13.

## Local Evidence

| Check | Evidence | Result |
|---|---|---|
| Current branch | `git branch --show-current` -> `main` | pass |
| Remote configured | `origin` -> `https://github.com/DmitryMatskevich/lanmaster-studio.git` | pass |
| Remote pushed | `git branch -vv` -> `main f60a3fb [origin/main]` | pass |
| GitHub repo exists | `gh repo view DmitryMatskevich/lanmaster-studio --json nameWithOwner,url,isPrivate` | pass, public |
| CI skeleton targets main | `.github/workflows/ci.yml` runs on `push` and `pull_request` to `main` | pass |
| CI executes verifier | `.github/workflows/ci.yml` runs `python3 scripts/verify_skeleton.py` | pass |
| Ownership metadata exists | `.github/CODEOWNERS` defines default owner `@lanmaster-studio/tech-leads` | pass |

## External Evidence

Initial branch-protection attempt failed while the repository was private:

```bash
gh api -X PUT repos/DmitryMatskevich/lanmaster-studio/branches/main/protection --input -
```

Result:

- HTTP 403
- GitHub message: `Upgrade to GitHub Pro or make this repository public to enable this feature.`

The repository was then made public by explicit command approval and branch
protection was applied with:

```bash
gh repo edit DmitryMatskevich/lanmaster-studio --visibility public --accept-visibility-change-consequences
gh api -X PUT repos/DmitryMatskevich/lanmaster-studio/branches/main/protection --input /private/tmp/lanmaster-studio-branch-protection.json
```

Read-back command:

```bash
gh api repos/DmitryMatskevich/lanmaster-studio/branches/main/protection --jq '{strict:.required_status_checks.strict,contexts:.required_status_checks.contexts,approvals:.required_pull_request_reviews.required_approving_review_count,codeOwners:.required_pull_request_reviews.require_code_owner_reviews,enforceAdmins:.enforce_admins.enabled,forcePushes:.allow_force_pushes.enabled,deletions:.allow_deletions.enabled,conversationResolution:.required_conversation_resolution.enabled}'
```

That first protection shape was active but blocked merge because a single-owner
repository has no separate reviewer/code-owner available. The enforceable final
P0 protection keeps required CI and branch-safety controls, but removes the
impossible self-review requirement.

Final read-back command:

```bash
gh api repos/DmitryMatskevich/lanmaster-studio/branches/main/protection --jq '{strict:.required_status_checks.strict,contexts:.required_status_checks.contexts,hasReviews:(.required_pull_request_reviews != null),enforceAdmins:.enforce_admins.enabled,forcePushes:.allow_force_pushes.enabled,deletions:.allow_deletions.enabled,conversationResolution:.required_conversation_resolution.enabled}'
```

Final read-back result:

```json
{"contexts":["Repository skeleton"],"conversationResolution":true,"deletions":false,"enforceAdmins":true,"forcePushes":false,"hasReviews":false,"strict":true}
```

Gate P0 protected-main evidence is satisfied.
