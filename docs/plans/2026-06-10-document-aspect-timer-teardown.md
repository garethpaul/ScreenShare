# Document Aspect Timer Teardown

## Status: Completed

## Context

Each document scheduled a repeating aspect-update timer with itself as the
target. The timer was not retained or invalidated when the window closed, so it
could keep retired document UI alive and continue periodic updates.

## Objectives

- Retain the repeating timer as document state.
- Replace any existing timer when preview setup runs again.
- Invalidate and release the timer before window capture teardown.

## Work Completed

- Added an optional `aspectTimer` property to `Document`.
- Invalidated an existing timer before scheduling a replacement.
- Invalidated and cleared the timer in `windowWillClose`.
- Extended static behavior checks and maintenance documentation.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`
