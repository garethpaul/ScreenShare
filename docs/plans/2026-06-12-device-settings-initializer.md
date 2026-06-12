# Device Settings Initializer

## Status: Completed

## Context

`Device(fromDevice:)` is declared failable even though it only forwards the
capture device's name and unique identifier to a nonfailable initializer.
`AppDelegate.findDeviceSettings` compensates by force-unwrapping the result,
creating an unnecessary crash surface when a newly discovered device has no
saved settings.

## Requirements

- R1. Make capture-device settings construction nonfailable.
- R2. Remove the force unwrap from new device-settings creation.
- R3. Preserve archive decoding as failable for malformed saved data.
- R4. Preserve device lookup, append, and return behavior.
- R5. Add source contracts, focused hostile mutations, documentation, and full
  `make check` verification.

## Scope Boundaries

- Do not change device discovery, archive format, or saved window geometry.
- Do not alter capture session or application-delegate ownership behavior.
- Do not claim connected-device runtime verification without compatible macOS
  hardware and an attached iOS capture device.

## Implementation Units

### Nonfailable live-device construction

**Files:** `ScreenShare/Device.swift`, `ScreenShare/AppDelegate.swift`

- Remove optionality from the live `AVCaptureDevice` convenience initializer.
- Construct and append new settings without a force unwrap.

### Regression contract and maintenance record

**Files:** `scripts/check-screenshare-source.py`, `README.md`, `SECURITY.md`,
`VISION.md`, `CHANGES.md`, `docs/plans/2026-06-12-device-settings-initializer.md`

- Reject failable live-device construction and forced result unwrapping while
  retaining failable archive decoding.

## Verification Plan

- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- focused initializer mutations
- `git diff --check`
- exact-head hosted unsigned macOS build before merge

## Work Completed

- Made the live `AVCaptureDevice` convenience initializer nonfailable.
- Removed the forced initializer result unwrap while preserving settings lookup,
  append, and return behavior.
- Kept `NSCoding` archive restoration failable and optional-bound for malformed
  saved data.
- Extended source contracts and maintenance guidance for both initializer
  domains.

## Verification

- `python3 scripts/check-screenshare-source.py --mode behavior` passed.
- Four focused hostile initializer mutations were rejected.
- `make check` passed; local Xcode compilation was unavailable on Linux and the
  Makefile ran its documented static-only path.
- An external-directory repository Makefile invocation passed from `/tmp`.
- `git diff --check` passed.

## Remaining Risks

- Static checks and compilation do not exercise real device connection,
  disconnection, or archived settings recovery.
