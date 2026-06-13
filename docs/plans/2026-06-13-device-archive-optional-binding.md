# Device Archive Optional Binding

## Status: Planned

## Context

`AppDelegate.loadDeviceSettings()` casts the local archive to `[Device]?`,
checks that the result is non-nil, and then force unwraps the same local value.
The current branch is guarded, but proof and use are separate statements at a
malformed local-data boundary that should remain fail-closed.

## Priority

A single optional binding keeps the decoded value scoped to the successful cast
and removes the remaining launch-time force unwrap without changing the
missing-archive fallback or active capture-device state.

## Objectives

- Optional-bind the `[Device]` archive result in one conditional.
- Preserve the empty saved-settings fallback for absent or malformed archives.
- Preserve active `devices` discovery and the `deviceSettingsLoaded` lifecycle.
- Add mutation-sensitive static coverage and synchronized documentation.

## Implementation Units

### U1. Bind decoded settings safely

**Files:** `ScreenShare/AppDelegate.swift`

Replace the nil comparison and forced use with `if let loaded = ... as?
[Device]`, assigning the bound value on success and `[]` on failure.

### U2. Preserve the archive contract

**Files:** `scripts/check-screenshare-source.py`, `README.md`, `VISION.md`,
`SECURITY.md`, `CHANGES.md`

Require one optional-binding archive load, reject `loaded!`, and document the
same fail-closed boundary. Add focused force-unwrap, missing-binding,
wrong-fallback, documentation, and plan-status mutations.

## Verification

- Focused behavior check and full `make check` locally and from outside the
  repository root.
- Hosted unsigned Xcode build through the pull-request event.
- Focused hostile mutations plus Python checker compilation, workflow YAML,
  plist/entitlements, asset JSON, SVG XML, secret, artifact, and
  `git diff --check` audits.

## Scope Boundary

This change does not migrate the legacy archive API, change archive location or
format, mutate active capture devices, or claim connected-device validation.
