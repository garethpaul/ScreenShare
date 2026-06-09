# Device Settings Log Privacy

## Status: Completed

## Context

`ScreenShare` stores local device settings so mirrored-device windows can
return to prior positions. `Device.savedSettingForOrientation` printed the
device name and saved window rectangle whenever it reused those settings.
Connected device names and window positions are useful local state, but they do
not need to be emitted to logs.

## Objectives

- Remove debug logging of saved device settings.
- Preserve local settings decoding and reuse behavior.
- Extend static behavior checks so device names and saved window rectangles are
  not logged from the settings path.
- Keep verification useful when Xcode is unavailable.

## Work Completed

- Removed saved-setting `print` calls from `Device.savedSettingForOrientation`.
- Extended `scripts/check-screenshare-source.py --mode behavior` to reject
  those debug logs.
- Updated README, VISION, and CHANGES notes for the privacy guard.

## Verification

- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`
