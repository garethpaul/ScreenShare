# Make Root Override Protection

## Status: Planned

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
