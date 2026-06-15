# Session Registration Guard

## Status: Completed

## Context

`AppDelegate.startNewSession` currently returns a `Skin` when the newly created
window has no content view. `refreshDevices` then records that detached skin as
an active device session even though it was never attached, registered, or
shown. The phantom entry blocks a later retry and leaves its capture session
running.

## Priority

High capture lifecycle resilience. A device session should become visible to
the session registry only after its window can host the capture view.

## Requirements

- Make device-session creation explicitly failable.
- Guard the window content view before constructing or starting the capture
  skin.
- Register a device session only after creation and attachment succeed.
- Preserve the single-device policy, capture setup, and window presentation.
- Add mutation-sensitive static contracts for failure ordering and conditional
  registration.

## Scope Boundaries

- Do not change capture input selection, archive encoding, project files,
  dependencies, or window layout calculations.
- Do not claim connected-device validation from Linux or unsigned hosted builds.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Return an optional skin from `startNewSession` and fail before skin creation
   when the window cannot provide a content view.
2. Store the new session only through optional binding in `refreshDevices`.
3. Extend source contracts and maintained documentation, then record completed
   verification evidence.

## Verification

- focused project and behavior source-contract validation
- repository and external-directory `make check`
- hostile return-type, guard-order, failure-return, and unconditional-registry
  mutations
- shell syntax, workflow YAML, plist, scheme XML, generated-artifact,
  credential-pattern, and exact-diff audits

## Verification Results

- Focused project and behavior source-contract validation passed.
- The repository and external-directory `make check` passed; Linux truthfully
  used the documented static-only path because `xcodebuild` is unavailable.
- Four hostile session-registration mutations were rejected across optional
  return type, guard ordering, nil failure return, and conditional registry
  state.
- Shell syntax, workflow YAML, Info and entitlements plists, shared scheme XML,
  generated-artifact, credential-pattern, conflict-marker, and exact-diff
  audits passed.

## Remaining Risks

- Connected-device capture and unusual AppKit window construction states still
  require manual validation on macOS with capture hardware.
