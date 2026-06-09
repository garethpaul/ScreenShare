# Video Height Change Detection

## Status: Completed

## Context

`Document.updateAspect()` should update preview dimensions when either the
captured video width or height changes. The height branch compared
`dimensions.height` to itself, so a height-only change could be ignored.

## Objectives

- Preserve existing preview aspect update behavior.
- Detect height-only video dimension changes.
- Add static behavior validation for the corrected comparison.
- Avoid broader Swift modernization in this focused pass.

## Work Completed

- Replaced the self-comparison with `dimensions.height != self.videoDimensions.height`.
- Extended `scripts/check-screenshare-source.py` to reject the old
  self-comparison and require the stored-height comparison.
- Updated README, VISION, and CHANGES notes for video height-change detection.

## Verification

- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Xcode Notes

`xcodebuild` was not available in this environment, so macOS build verification
was not run here. The repository `make check` wrapper still runs `xcodebuild`
when that tool is available locally.
