# App Stdout Logging Guard

## Status: Completed

## Context

`ScreenShare` already guards saved device names and window rectangles from
being logged. Other capture lifecycle paths still emitted ad hoc stdout logs for
session start/stop events, device connection changes, and selected skin names.
Those logs are not needed for the user-facing mirroring flow and can add noise
or device context to shared diagnostic output.

## Objectives

- Remove nonessential stdout logging from capture lifecycle and device event
  observers.
- Preserve explicit runtime-error diagnostics for malformed capture
  notifications and save failures.
- Extend static verification so app Swift sources do not reintroduce active
  `print` or `println` logging.

## Work Completed

- Removed session start/stop, device connect/disconnect, one-session, and
  resolution debug prints from `AppDelegate` and `Document`.
- Removed selected skin-name debug logging from `Skin`.
- Extended `scripts/check-screenshare-source.py` to reject active app
  `print`/`println` calls and selected skin-name `NSLog`.
- Documented the stdout logging guard in README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Replace remaining diagnostic `NSLog` calls with a structured logging wrapper
  in a dedicated compatibility pass.
- Review force unwraps in window and preview-layer setup once an Xcode build
  environment is available.
