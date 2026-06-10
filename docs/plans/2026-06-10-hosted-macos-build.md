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
- Added workflow concurrency cancellation so superseded branch runs stop.
- Made Makefile paths resolve from the repository root even when invoked from
  another working directory.
- Extended static checks and documentation to preserve the hosted build gate.

## Verification

- `make check`
- `make -f /path/to/ScreenShare/Makefile check` from outside the repository
- `git diff --check`
- GitHub Actions `contract` and `build` jobs
