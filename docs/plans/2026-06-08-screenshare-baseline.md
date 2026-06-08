# ScreenShare Baseline

## Status: Completed

## Context

`ScreenShare` is a macOS demo tool for mirroring a connected iOS device into a
desktop window. The maintenance baseline should keep shell/Xcode project
metadata, capture privacy prompts, and runtime-error handling visible even when
Xcode is unavailable locally.

## Objectives

- Preserve the connected-device mirroring flow and shared Xcode schemes.
- Keep the camera entitlement paired with an explicit usage description.
- Validate capture runtime-error observers without force-unwrapped metadata.
- Keep shell build syntax portable under its `/bin/sh` shebang.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs shell syntax, project, behavior, and optional
  Xcode build checks.
- Added canonical `docs/plans` coverage for the current mirroring baseline.
- Extended project checks to require completed `docs/plans` entries with
  `make check` verification.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `sh -n build.sh`
- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Run the shared Xcode schemes on macOS with a connected iOS device.
- Add manual verification notes for connect/disconnect and runtime-error
  handling.
