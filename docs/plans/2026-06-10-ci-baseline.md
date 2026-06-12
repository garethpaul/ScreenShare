# CI Baseline

Status: Completed

## Context

The repository had a local static `make check` baseline for shell syntax,
Xcode metadata, camera permission, runtime-error, and capture UI guardrails,
but no hosted workflow ran it for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Extended the project checker and docs so the hosted CI path stays visible.

## Verification

- `make check`
