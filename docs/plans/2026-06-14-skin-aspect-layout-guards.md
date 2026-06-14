# Skin Aspect Layout Guards

## Status: Completed

## Context

Skin preview creation and resize-notification registration now guard optional
AppKit state. The later aspect-layout path still force unwraps the owning window,
its screen, and nib-backed view outlets, so device-dimension updates can crash
when a window is detached or skin loading is incomplete.

## Priority

High capture UI reliability. Aspect recalculation runs during device setup and
format changes and must fail closed at AppKit lifecycle boundaries.

## Requirements

- Guard the owning window before aspect layout and pass that nonoptional value
  through layout helpers.
- Tolerate a missing window screen without force unwrapping or crashing.
- Guard the skin view, device frame image, and preview view before resizing.
- Preserve saved device positioning, scale-to-fit behavior, centering, shadow
  invalidation, and successful capture preview layout.
- Add fail-closed source contracts and keep maintained documentation and
  completed verification evidence aligned.

## Scope Boundaries

- Do not change mouse interaction, capture-device switching, archive settings,
  session policy, nib contents, or supported macOS/Xcode versions.

## Implementation Units

1. Bind the aspect-layout window once and use an optional screen frame for
   scaling and centering.
2. Pass guarded window state into positioning and view-layout helpers and bind
   required nib outlets before mutation.
3. Extend source contracts and maintained documentation for the layout boundary
   and completed validation evidence.

## Verification

- focused project and behavior source contracts
- repository and external-directory `make check`
- hostile window, screen, outlet, helper, documentation, and plan mutations
- hosted unsigned macOS build on the exact pull-request head
- generated-artifact, credential-pattern, and exact-diff audits

## Verification Results

- Focused project and behavior source contracts passed with one guarded window
  and outlet binding, optional screen fallback, and nonoptional helper inputs.
- The repository and external-directory `make check` passed; Linux truthfully
  used the static-only boundary because `xcodebuild` is unavailable.
- Six hostile Skin aspect-layout mutations were rejected across window binding,
  screen fallback, outlet binding, helper handoff, documentation, and completed
  plan status.
- Final generated-artifact, credential-pattern, and exact-diff audits passed
  with only the intended Skin, checker, documentation, and plan changes.
- Hosted unsigned macOS compilation remains required on the exact pushed head.

## Risks

- Linux validation is static-only; AppKit API compatibility requires the hosted
  macOS/Xcode build.
- Nib loading, physical-device mirroring, and live window movement still require
  manual macOS hardware validation.
