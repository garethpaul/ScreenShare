# Document Preview Guard

## Status: Completed

## Context

`Document.windowControllerDidLoadNib(_:)` and `Document.updateAspect()` still
used active force unwraps around preview outlets, backing layers, capture input
ports, and the document window. The app already handled malformed capture error
metadata, but missing nib or capture state could still crash before those
guards mattered.

## Objectives

- Guard the document preview outlet and backing layer before adding the capture
  preview layer.
- Optional-bind the capture input port, document window, and format
  description before calculating aspect changes.
- Keep the existing resolution fallback text when aspect calculation cannot
  run.
- Add static checks so the guarded path does not regress.

## Work Completed

- Added early fallback logging when the document preview outlet or backing
  layer is missing.
- Replaced the `updateAspect()` input-port and window force unwrap path with a
  single guarded aspect calculation.
- Added `resetResolutionStatus()` to centralize the resolution fallback state.
- Extended `scripts/check-screenshare-source.py` to reject the old force unwraps
  and require the new optional-binding path.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `git diff --check`

`xcodebuild` is not installed in this environment, so `make check` reports that
the Xcode build was not run after static verification passes.

## Follow-Up Candidates

- Continue reducing legacy force unwraps in `Skin` window sizing and input-port
  retry paths.
- Run a connected-device manual pass on macOS with Xcode to verify preview
  setup and aspect changes.
