# Hosted macOS Build

Status: Completed

## Context

The existing GitHub Actions workflow enforced portable source and privacy
contracts on Linux, but it could not prove that the legacy Xcode project still
compiled. The workflow also used a moving Ubuntu runner label, which made the
hosted toolchain less predictable.

## Changes

- Fixed the portable contract job to Ubuntu 24.04.
- Added a bounded macOS 15 job that builds the shared app scheme with code
  signing disabled.
- Updated unsupported Swift 2.3 and macOS 10.9 project settings to Swift 5 and
  macOS 10.13 so Xcode 16 can evaluate the source.
- Migrated the first compiler-blocking Swift 2 APIs for notifications, coding,
  application access, retry counters, and mouse event overrides.
- Migrated keyed archives, AVFoundation and AppKit names, formatting helpers,
  and CoreMediaIO size calculation exposed by the next compiler pass.
- Corrected Swift 5 external labels and delegated the `NSSize` convenience
  initializer through its designated initializer.
- Migrated the capture skin's framework constants, event properties, dispatch
  calls, labels, and optional input handling to current Swift APIs.
- Migrated the parallel document capture path to current AVFoundation, AppKit,
  timer, dispatch, and input-construction APIs.
- Added workflow concurrency cancellation so superseded branch runs stop.
- Made Makefile paths resolve from the repository root even when invoked from
  another working directory.
- Extended static checks and documentation to preserve the hosted build gate.

## Verification

- `make check`
- `make -f /path/to/ScreenShare/Makefile check` from outside the repository
- `git diff --check`
- GitHub Actions `contract` and `build` jobs
