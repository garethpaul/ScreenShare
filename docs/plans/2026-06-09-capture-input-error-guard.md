# Capture Input Error Guard

## Status: Completed

## Context

`Document.selectedDevice` creates an `AVCaptureDeviceInput` and calls
`displayError(error)` if input creation fails. `displayError` force-unwrapped
the optional `NSError`, so a failure without metadata could crash while the app
was already trying to report a capture setup problem.

## Objectives

- Preserve the existing user-facing `presentError` path when an `NSError`
  exists.
- Handle missing capture input error metadata without force unwrapping.
- Keep malformed input-error notifications observable through diagnostics.
- Extend static validation so the optional-error guard remains in place.

## Work Completed

- Added a `guard let error = error else` path in `Document.displayError`.
- Logged missing capture input `NSError` metadata with `NSLog`.
- Removed the forced optional cast before `presentError`.
- Extended `scripts/check-screenshare-source.py --mode behavior` to reject the
  force unwrap and require the missing-metadata diagnostic.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `python3 scripts/check-screenshare-source.py --mode behavior`
  failed before the Swift fix because `displayError` still force-unwrapped the
  optional `NSError`.
- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Xcode Notes

`xcodebuild` was not available in this environment, so macOS build verification
was not run here. The repository `make check` wrapper still runs `xcodebuild`
when that tool is available locally.
