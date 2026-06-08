# Device Archive Decoding

## Status: Completed

## Context

`ScreenShare` stores connected-device window settings with `NSCoding`.
`Device.init(coder:)` force-cast every archived value, so a corrupt or outdated
local settings file could crash the app while loading device preferences.

## Objectives

- Preserve the existing archived settings keys and `Device` model shape.
- Decode saved settings with optional binding instead of force casts.
- Return `nil` for malformed archives so callers can continue with defaults.
- Extend static behavior checks to preserve safe archive decoding.

## Work Completed

- Replaced `as! String` archive field casts with a `guard let` decode block.
- Converted saved rect strings after validation.
- Extended `scripts/check-screenshare-source.py` to reject force-cast device
  archive decoding.
- Updated README, VISION, and CHANGES.

## Verification

- `sh -n build.sh`
- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Move the `devices` settings archive into Application Support with a migration
  note.
- Add manual verification notes for corrupted settings recovery when Xcode is
  available.
