# Skin Application Delegate Guard

## Status: Completed

## Context

Every `Skin` instance force-cast the shared application delegate during object
initialization. Nib loading, previews, tests, or unusual application lifecycle
state could therefore crash before capture setup or teardown had a chance to
handle the missing coordinator.

## Objectives

- Preserve application-delegate selection and device-settings coordination.
- Avoid force-casting the shared application delegate during `Skin` setup.
- Log unavailable delegate state while allowing local capture teardown to run.
- Add deterministic static checks for every delegate interaction.

## Work Completed

- Replaced the stored force-cast delegate with a guarded computed property.
- Made selection and settings interactions use optional delegate chaining.
- Added a clear diagnostic when the expected application delegate is absent.
- Extended the behavior checker and maintenance documentation.

## Verification

- `python3 scripts/check-screenshare-source.py --mode project`
- `python3 scripts/check-screenshare-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`
