# CI Baseline

Status: Completed

## Context

The repository had a local static `make check` baseline for shell syntax,
Xcode metadata, camera permission, runtime-error, and capture UI guardrails,
but no hosted workflow ran it for pushes and pull requests. Linux CI cannot
compile or exercise the macOS capture path, so the hosted result is explicitly
limited to portable source and privacy contracts.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Pinned Node 24-compatible checkout and Python setup actions by verified SHA.
- Restricted workflow permissions to read-only contents and bounded the job to
  five minutes while disabling checkout credential persistence.
- Extended the project checker and docs so the hosted CI path stays visible.

## Verification

- `python3 -m py_compile scripts/check-screenshare-source.py`
- `make check`
- `git diff --check`
