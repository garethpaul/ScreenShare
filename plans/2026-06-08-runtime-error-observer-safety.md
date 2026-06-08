# Runtime Error Observer Safety

## Problem

Both capture runtime-error observers force-unwrapped notification `userInfo`
and capture error metadata. If AVFoundation delivered a malformed notification,
the app could crash while trying to report a capture-session error.

## TDD Evidence

1. Extended `scripts/check-screenshare-source.py --mode behavior` to reject
   `userInfo!` and force-cast `NSError` extraction in runtime-error observers.
2. Required both the app-level and document-level observers to optional-bind
   `AVCaptureSessionErrorKey` as `NSError`.
3. Added fallback logging when a runtime-error notification arrives without
   expected error metadata.

## Verification

- `make lint`
- `make test`
- `make verify`
- `git diff --check`

`make build` runs the shared Xcode scheme when `xcodebuild` is installed;
otherwise it reports that static checks completed.
