# Skin Device Switch Rollback

Status: In Progress

## Problem

`Document.selectedDevice` protects capture input replacement with construction,
admission, and rollback checks, but `Skin.selectedDevice` still removes the
working input first and calls `addInput` without `canAddInput`. Construction or
admission failure can therefore leave a skin session detached from its prior
capture device.

## Requirements

1. Construct a requested replacement input before mutating the skin capture
   session.
2. Keep device replacement inside one balanced configuration transaction.
3. Validate replacement admission with `canAddInput` before adding it.
4. Restore the prior input when replacement construction or admission fails.
5. Preserve nil-device removal, format-change observation, saved device
   settings, aspect updates, selection state, session lifetime, and window UI.
6. Log generic failures without device identifiers or other metadata.
7. Add mutation-sensitive static contracts, synchronized guidance, and
   truthful completion evidence.

## Implementation Units

### 1. Make skin input replacement transactional

File: `ScreenShare/Skin.swift`

Capture the prior input, prepare the replacement before configuration, remove
the old input only after preparation, validate admission, and restore the prior
input on rejection while preserving the existing success follow-up work.

### 2. Protect rollback parity

Files:

- `scripts/check-screenshare-source.py`
- `docs/plans/2026-06-16-skin-device-switch-rollback.md`

Require method-scoped preparation ordering, one configuration transaction,
admission checks, rollback, generic logging, nil-device behavior, guidance, and
completed-plan evidence.

### 3. Document both switch boundaries

Files:

- `AGENTS.md`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Record that both document and skin capture paths preserve the prior working
input when a replacement cannot be constructed or admitted.

## Verification Plan

- Capture the pre-change ordering and missing-admission-check evidence.
- Run repository and external-directory `make check`.
- Reject hostile preparation, admission, rollback, transaction, logging,
  guidance, and plan-status mutations.
- Audit the exact diff, Swift conflict markers, generated artifacts, modes,
  whitespace, and credential patterns before shipping.
- Capture one bounded exact-head hosted snapshot after push without polling.

## Scope Boundaries

- Do not change device discovery, one-device policy, session registration,
  pointer handling, aspect layout, archive format, entitlements, or Xcode
  project settings.
- Do not expose device identifiers in logs.
- Do not claim local Xcode, camera-device, capture-session, or UI execution on
  Linux.
- The successor PR will be stacked on open PR #16; neither pull request may be
  merged or closed without explicit authorization.
