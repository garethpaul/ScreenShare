# Make Authority Isolation

## Status: Completed

## Context

The protected repository root stopped direct `ROOT=/tmp` redirection. Once the
checked-in Makefile begins evaluation, it can also pin recipe shells, Python
commands, Xcode build commands, bytecode settings, and its repository root.
GNU Make preload files and additional `-f` programs are different: they are
evaluated during startup, before an in-Makefile guard can establish authority.

## Requirements

- **R1:** Fail closed when startup metadata already exposes preload or earlier
  Makefiles, and document that their code may already have executed.
- **R2:** Derive the checkout root safely from the exact Makefile path.
- **R3:** Fix the shell, Python command, Xcode build command, and bytecode
  suppression.
- **R4:** Exercise every public target across hostile authority inputs.
- **R5:** Preserve all Swift, project, capture, settings, and signing behavior.

## Implementation

- Hardened recipe authority from the point the checked-in Makefile is evaluated.
- Added a macOS-portable `root-test` checkout with spaces, quotes, and
  command-substitution syntax in its path.
- Covered all six public targets across eleven authority modes, explicit
  file-list rejections, and the GNU Make startup boundary for `MAKEFILES`,
  earlier `-f`, and later `-f` programs.
- Left Swift source, Xcode project, entitlements, and application behavior
  unchanged.

## Verification

- `make root-test` passed 66 target/authority cases, two metadata rejection
  cases, and three startup-boundary cases.
- `make check` passed from the repository and through an absolute Makefile path.
- Python and shell syntax checks, `git diff --check`, and repository integrity
  screening passed.

## Trust Boundary

The checked-in Makefile cannot make an already-started GNU Make process safe
against caller-supplied programs. A `MAKEFILES` preload or an earlier `-f`
program can execute while GNU Make is loading files, before this Makefile can
reject the visible metadata. A later `-f` program can replace recipes after
this Makefile has been read. Trusted automation must therefore invoke this
Makefile without `MAKEFILES` or additional `-f` arguments; the guards diagnose
misuse but are not a sandbox for hostile GNU Make startup inputs.
