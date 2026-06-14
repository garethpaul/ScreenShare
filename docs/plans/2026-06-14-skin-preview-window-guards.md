# Skin Preview And Window Guards

## Status: Planned

## Context

`Skin.loadSkinFromNib()` force unwraps the preview backing layer and generated
video preview layer, while `registerNotifications()` force unwraps the owning
window both when registering and when handling resize events. Missing or late
IBOutlet/window state can therefore crash instead of failing closed.

## Priority

High capture UI reliability. Legacy nib and window lifecycle boundaries must
not crash the process when optional AppKit state is unavailable.

## Requirements

- Guard the preview outlet and backing layer before configuring video preview.
- Use a locally created preview layer without force unwrapping optional state.
- Guard the notification window and tolerate its later release.
- Preserve successful skin loading, resize behavior, and capture session use.
- Add fail-closed source contracts, documentation, and mutation coverage.

## Verification

- focused project and behavior source contracts
- repository and external-directory `make check`
- hostile outlet, layer, window, closure, documentation, and plan mutations
- hosted unsigned macOS build on the exact pull-request head
- generated-artifact, credential-pattern, and exact-diff audits
