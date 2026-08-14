# P5-10 Commit, Revision, History And Release UI

## Scope

P5-10 adds the first frontend control surface for turning a preview draft into an
immutable revision, reviewing revision history, and queueing a release from a
committed revision.

## Implemented

- Added a `CommitReleasePanel` to the model workspace after preview and diff QA.
- Commit action reads the live draft token and calls the draft commit API with a
  PMD payload assembled from the current property editor state.
- Release action is guarded so draft-only state cannot be released.
- Revision history can be loaded from the model revisions endpoint and shows
  revision IDs plus content hashes.
- Newly committed revisions become immediately releasable in the UI without a
  full page reload.

## Verification

- Frontend static verifier checks the commit, release, release guard and history
  UI contract.
- API regression keeps draft commit and release orchestration covered by backend
  tests.
- Web smoke confirms the built frontend bundle is served by FastAPI and includes
  the P5-10 UI strings.
