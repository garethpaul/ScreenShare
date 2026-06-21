# Make Authority Isolation

## Status: Completed

## Context

The protected repository root stopped direct `ROOT=/tmp` redirection, but GNU
Make still accepted caller-controlled preload files, file lists, recipe shells,
Python commands, and Xcode build commands. Those channels could replace static
contracts or turn the hosted native build into a no-op.

## Requirements

- **R1:** Load the repository Makefile alone and reject overridden file lists.
- **R2:** Derive the checkout root safely from the exact Makefile path.
- **R3:** Fix the shell, Python command, Xcode build command, and bytecode
  suppression.
- **R4:** Exercise every public target across hostile authority inputs.
- **R5:** Preserve all Swift, project, capture, settings, and signing behavior.

## Implementation

- Hardened Make authority before target definitions are evaluated.
- Added a macOS-portable `root-test` checkout with spaces, quotes, and
  command-substitution syntax in its path.
- Covered all six public targets across eleven authority modes plus explicit
  file-list, preload, and multiple-Makefile rejection cases.
- Left Swift source, Xcode project, entitlements, and application behavior
  unchanged.

## Verification

- `make root-test` passed 66 target/authority cases and four rejection cases.
- `make check` passed from the repository and through an absolute Makefile path.
- Python and shell syntax checks, `git diff --check`, and repository integrity
  screening passed.
