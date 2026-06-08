# Build And Privacy Gate

## Problem

The repository had Xcode targets but no portable repo-local verification command.
The checked-in `build.sh` used bash function syntax under a `/bin/sh` shebang,
and the app had camera capture entitlement/source code without an
`NSCameraUsageDescription` prompt string.

## TDD Evidence

1. Ran `sh -n build.sh` and confirmed the script failed before reaching Xcode.
2. Confirmed `NSCameraUsageDescription` was absent from `ScreenShare/Info.plist`
   while the app uses `AVCaptureDevice` and declares the camera entitlement.
3. Added static project and behavior checks, fixed the shell syntax and privacy
   metadata, then reran the full verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
