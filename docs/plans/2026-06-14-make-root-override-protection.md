# Make Root Override Protection

## Status: Completed

## Context

The Makefile derives its repository root and uses that path for shell syntax,
static source contracts, and conditional Xcode builds. GNU Make command-line
variables outrank an ordinary assignment, so `make ROOT=/tmp check` can
redirect those commands away from the checkout.

## Requirements

- **R1:** Prevent command-line and environment values from replacing the
  Makefile-derived repository root.
- **R2:** Keep `PYTHON` and `XCODEBUILD` configurable.
- **R3:** Require exactly one protected root declaration in the source checker.
- **R4:** Preserve the declaration's existing Makefile position while proving
  every public alias from root and an external directory.
- **R5:** Preserve capture, device settings, archive decoding, rollback,
  workflow, signing, shell, and macOS build contracts.

## Implementation Units

### U1. Protected Root

Give the existing repository-derived root assignment override precedence
without reordering tool variables or changing recipes.

### U2. ScreenShare Contract

Extend `scripts/check-screenshare-source.py` to reject weakened, duplicate, or
caller-controlled root declarations and incomplete evidence.

### U3. Verification

Run project and behavior contracts, shell syntax, all Make aliases, external
hostile execution, Python 3.12 validation, mutations, and integrity screening.

## Scope Boundary

- Do not modify Swift, shell behavior, projects, schemes, or signing settings.
- Do not change hosted actions, runners, Xcode build, or test coverage.
- Do not add archives, recordings, DerivedData, caches, or credentials.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- external `make ROOT=/tmp check`
- root-declaration, checker, plan-status, README-index, and evidence mutations
- Python/shell syntax, workflow YAML, protected-file, secret, artifact, and
  `git diff --check` gates

## Work Completed

- Protected the existing Makefile-derived repository root in place from
  command-line and environment overrides.
- Added exact-count, completed-evidence, and README-index contracts.
- Preserved all Swift, shell, capture, settings, archive, project, workflow,
  and hosted macOS build boundaries.

## Verification Results

- `python3 scripts/check-screenshare-source.py --mode project` and
  `python3 scripts/check-screenshare-source.py --mode behavior` both passed.
- From both the checkout and an external directory, all five public Make aliases passed.
- `make ROOT=/tmp check` passed externally while still executing repository-owned
  shell, project, and behavior contracts.
- Python 3.12 passed the full static gate; local Xcode compilation was skipped
  because `xcodebuild` was unavailable, leaving the hosted macOS build authoritative.
- Six hostile mutations were rejected across root declaration, checker
  expectation, plan status, README indexing, and recorded evidence.
- Python and shell syntax, workflow YAML, exact-base protected-file comparison,
  secret screening, generated-artifact screening, and `git diff --check`
  passed before shipping.
