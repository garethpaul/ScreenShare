# Main Window Refresh Guard

## Status: Completed

## Context

`AppDelegate.refreshDevices()` reconciles connected capture devices and then
hides the main device-list window when a mirrored-device session is active. That
last step force-unwrapped the main window outlet, so a missing or not-yet-loaded
window could crash during device refresh instead of logging a clear fallback.

## Objectives

- Preserve the existing hide/show behavior for the main device-list window.
- Avoid force-unwrapping the main app window outlet during device refresh.
- Add deterministic static checks for the guarded refresh path.

## Work Completed

- Guarded `self.window` before hiding or showing the main device-list window.
- Logged a clear fallback when the main window outlet is unavailable.
- Extended `scripts/check-screenshare-source.py --mode behavior` to reject the
  force unwrap and require the guarded path.
- Updated README, VISION, and CHANGES notes for the main-window refresh guard.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make lint`
- `make check`
- `make verify`
- `git diff --check`

`xcodebuild` is not installed in this environment, so `make check` reports that
the Xcode build was not run after static verification passes.
