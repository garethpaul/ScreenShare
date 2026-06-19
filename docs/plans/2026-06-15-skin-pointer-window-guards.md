# Skin Pointer and Window Guards

## Status: Completed

## Context

The Skin preview and aspect-layout paths now guard optional AppKit state, but
mouse movement and device-settings persistence still force-unwrap the window,
preview image outlet, stored pointer origin, main screen, and device settings.
Those callbacks can outlive outlet or window availability during teardown.

## Priority

High UI lifecycle resilience. Pointer and resize callbacks should fail closed
instead of crashing when AppKit state disappears.

## Requirements

- Guard the mouse-down window and preview-image outlet before calculating resize
  state.
- Guard the stored pointer origin and window during drag callbacks.
- Clamp movement only when a window or main screen frame is available.
- Guard window and device settings before persisting orientation-specific frames.
- Preserve capture, aspect layout, resize behavior, device switching, and archive
  format.
- Add fail-closed static and mutation-sensitive contracts.

## Scope Boundaries

- Do not change capture session setup, device archive encoding, project files,
  dependencies, or window aspect calculations.
- Do not claim connected-device or interactive pointer validation from Linux or
  unsigned hosted builds.
- Do not merge or close stacked pull requests without explicit authorization.

## Implementation Units

1. Replace pointer-handler force unwraps with guarded local window, outlet,
   pointer-origin, and optional screen values.
2. Guard device-settings persistence with local nonoptional settings and window
   values.
3. Extend source contracts, maintained documentation, and completed evidence.

## Verification

- focused project and behavior source-contract validation
- repository and external-directory `make check`
- hostile pointer-window, pointer-origin, screen, settings, documentation, and
  completed-plan mutations
- shell syntax, workflow YAML, plist, scheme XML, generated-artifact,
  credential-pattern, and exact-diff audits

## Verification Results

- Focused project and behavior source-contract validation passed.
- The repository and external-directory `make check` passed; Linux truthfully
  used the documented static-only path because `xcodebuild` is unavailable.
- Six hostile Skin pointer mutations were rejected across pointer-window,
  pointer-origin, screen, settings, documentation, and completed-plan state.
- Shell syntax, workflow YAML, Info and entitlements plists, shared scheme XML,
  generated-artifact, credential-pattern, conflict-marker, and exact-diff
  audits passed.

## Remaining Risks

- Connected-device capture, interactive dragging, and live resize behavior still
  require manual validation on macOS with available capture hardware.
- Hosted unsigned compilation proves source compatibility but does not exercise
  AppKit teardown timing or pointer callbacks.
