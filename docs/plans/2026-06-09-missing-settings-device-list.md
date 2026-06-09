# Missing Settings Device List

## Status: Completed

## Context

`AppDelegate.loadDeviceSettings()` loads saved window settings for known
devices. When no archive existed, the fallback cleared `devices` instead of
`deviceSettings`, which could mutate the active capture-device list while
handling local settings state.

## Objectives

- Preserve the local device-settings archive behavior.
- Keep active capture-device discovery separate from saved settings state.
- Reset saved settings to an empty list when no archive exists.
- Add static behavior validation for the fallback path.

## Work Completed

- Changed the missing-archive fallback to clear `deviceSettings` instead of
  `devices`.
- Extended `scripts/check-screenshare-source.py` to reject the old fallback and
  require the saved-settings reset.
- Updated README, VISION, and CHANGES notes for the missing-settings guard.

## Verification

- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `git diff --check`

## Xcode Notes

XcodeBuildMCP was not available in this environment, so macOS app automation was
not run here. The repository `make check` wrapper still runs `xcodebuild` when
that tool is available locally.
