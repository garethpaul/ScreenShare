# Capture Device Switch Rollback

## Status: Completed

## Context

`Document.selectedDevice` removed the active capture input before constructing
the replacement and called `addInput` without `canAddInput`. Construction or
session-admission failure could therefore leave a previously working preview
without any input. Device refresh also wrapped the setter in a second session
configuration transaction.

## Priority

Capture device switching should be transactional. A failed replacement must
not destroy the current working session, and session configuration should not
depend on nested begin/commit calls.

## Objectives

- Construct the replacement input before mutating the session.
- Use one begin/commit configuration transaction per switch.
- Check `canAddInput` before adding a replacement.
- Restore the previous input when replacement admission fails.
- Log a fixed diagnostic without exposing device names or identifiers.
- Add fail-closed source, documentation, and completed-plan contracts.

## Work Completed

- Prepared replacement inputs before capture-session mutation.
- Centralized commit and aspect refresh in a `defer` block.
- Added replacement admission validation and prior-input rollback.
- Removed nested session configuration from device refresh.
- Extended the static checker and project guidance.

## Verification

- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check` locally and from outside the repository root
- focused construction, admission, rollback, transaction, documentation, and
  plan mutations
- Python checker compilation, plist/asset parsing, Swift delimiter, secret,
  artifact, and `git diff --check` audits
- hosted unsigned macOS compilation; connected-device behavior remains manual

Project and behavior checks plus full `make check` passed locally with the
documented static-only path because `xcodebuild` is unavailable. All six
construction, admission, rollback, transaction, documentation, and plan
mutation categories were rejected.

The app plist, entitlements, both README SVG files, and all nine asset JSON
manifests parsed successfully. Python checker compilation, high-confidence
secret screening, and `git diff --check` passed. Checker compilation created an
ignored `scripts/__pycache__` artifact; it is excluded from the explicit-path
commit and preserved. Hosted unsigned compilation remains required on the
exact PR head.

## Scope Boundary

This preserves the prior input when a replacement is rejected. It does not
exercise connected iOS hardware, capture output, mirroring latency, or device
disconnect timing in hosted CI.
