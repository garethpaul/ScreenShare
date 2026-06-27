# Changes

## 2026-06-27 - P1 - Select capture video ports explicitly

### Summary

Stopped Document and Skin aspect handling from treating the first capture input
port as video when a muxed device can expose separate media streams.

### Work completed

- Added a shared `.video`-filtered `AVCaptureDeviceInput.videoPort` selector.
- Document and Skin select the explicit video port instead of relying on
  capture input port ordering.
- Routed both format observers and both dimension readers through that selector.
- Added a red-first behavior contract and a hostile unfiltered-port mutation.
- Synchronized maintained runtime and security guidance.

### Evidence

- Apple AVFoundation documentation states that a capture input can provide one
  or more streams and represents each stream with its own input port.
- The focused gate failed before implementation on the missing selector and all
  four `ports.first` call sites, then passed with 11 mutation tests.
- `make check` passed 66 Make target/authority cases, project and behavior
  checks, and all 11 mutation tests from the checkout and `/tmp`.
- Python compilation, shell syntax, and `git diff --check` passed.
- Native Xcode compilation is unavailable on this Linux host; hosted unsigned
  macOS compilation remains required on the exact PR head.

### Blockers

- Live muxed-device ordering and format transitions still require compatible
  trusted iPhone/iPad hardware; hosted builds validate compilation only.

### Next action

- Run complete local and hosted verification, review the exact head, and merge
  only if every maintained gate remains green.

## 2026-06-26 06:52 PDT - P2 - replace document aspect polling

### Summary

Replaced the document preview's repeating one-second aspect timer with the
active capture input port's format-change notification, preserving an immediate
refresh after session start and safe observer replacement during device swaps.

### Work completed

- Added a dedicated document format-observer owner that follows the existing
  Skin lifecycle precedent.
- Document aspect updates run once after session start and then only for the
  active input port's format-change notifications; device switches replace the
  observer and window teardown removes it.
- Replaced observers after successful, cleared, and rolled-back device
  transactions and removed them during window teardown.
- Added scoped source contracts, three hostile mutations, design evidence, and a
  completed implementation plan.

### Threads

- None; current source, history, Apple AVFoundation documentation, tests, and
  the existing Skin observer pattern were reviewed directly.

### Files changed

- `ScreenShare/Document.swift` — event-driven aspect updates.
- `scripts/check-screenshare-source.py` and
  `scripts/test-screenshare-contracts.py` — regression and mutation coverage.
- `AGENTS.md`, `README.md`, `SECURITY.md`, and `VISION.md` — maintained behavior
  contract.
- `docs/plans/2026-06-26-document-format-observer-design.md` and
  `docs/plans/2026-06-26-document-format-observer.md` — design and execution
  evidence.

### Validation

- RED focused behavior gate — rejected the timer and missing observer lifecycle.
- GREEN focused behavior gate — passed after the notification implementation.
- Three isolated observer/guidance-removal mutations — rejected.
- `make check` and an external absolute-Make invocation — passed 66 Make
  target/authority cases, project and behavior checks, and 10 Python mutation
  tests; local Xcode compilation skipped because `xcodebuild` is unavailable.
- Hosted unsigned macOS compilation — required before merge.

### Bugs / findings

- P2 efficiency/lifecycle: the document woke every second indefinitely even
  though AVFoundation exposes the exact format-change event.

### Blockers

- Physical-device orientation changes still require manual iPhone/iPad
  verification; hosted compilation cannot exercise that hardware boundary.

### Next action

- Run complete local and hosted verification, then merge only the reviewed
  exact head.

## 2026-06-26

### ScreenShare device setup and lifecycle guide

- Completed three ScreenShare device-documentation priorities with source-backed
  macOS/Xcode setup, camera permission, CoreMediaIO device registration,
  single-session admission, connect/disconnect, local-data, and verification
  guidance.
- Added fail-closed documentation contracts and a completed implementation plan
  so future edits cannot silently remove the operating boundaries.

Validation:

- Rejected 19 isolated hostile documentation mutations spanning every new
  README contract, the maintained roadmap boundary, this history entry, and the
  completed plan status.
- Passed `/usr/bin/make check` from the checkout and from an unrelated working
  directory. Each invocation passed 66 Make target/authority cases, one dollar-
  syntax checkout case, two `MAKEFILE_LIST` rejections, three documented GNU
  Make startup-boundary cases, project checks, behavior checks, and seven Python
  contract tests.
- Audited the guide against the checked-in entitlement and usage plist, Swift
  registration/filter/session/notification/archive code, Xcode deployment
  settings, and pinned Ubuntu/macOS workflow jobs.

Blocker:

- Physical-device trust, Camera authorization, live mirroring, disconnect, and
  reconnect verification still require an unlocked iPhone or iPad and cannot be
  demonstrated by the current Linux checkout or hosted native build alone.

## 2026-06-21

- Isolated checked-in Make recipes from caller-controlled shells, Python
  commands, Xcode builders, bytecode settings, and repository roots, with 66
  target/authority cases. Documented that `MAKEFILES` and additional `-f`
  programs execute at GNU Make startup outside an in-Makefile trust boundary.
- Pinned the documented native unit-test script and hosted Xcode probe to
  `/usr/bin/xcodebuild` so caller `PATH` cannot replace application validation.

## 2026-06-19

- Initialized each Skin capture session before nib-backed preview setup and
  removed the duplicate preview-layer construction path.
- Replaced accumulated format-change observers when devices switch or retry.
- Rejected non-finite and non-positive saved or computed window geometry.
- Guarded pointer hover callbacks when the resize-handle outlet is unavailable.
- Made the documented unsigned macOS unit-test wrapper executable on current
  Xcode by separating the test module name and updating the XCTest measure API.
- Added seven hostile repository-copy mutations covering the reviewed runtime
  and Xcode contracts, and reconciled the useful run guidance from PR #7.

## 2026-06-17

- Initial Skin sessions reject unattached capture devices before window and
  view attachment.

## 2026-06-16

- Skin capture device switch rollback preserves the prior working input when a
  replacement cannot be constructed or admitted.

## 2026-06-15

- Made device-session creation failable so a missing window content view cannot
  leave a detached capture skin registered as an active session.
- Added Skin pointer and window guards for movement and device-settings
  persistence when AppKit state is unavailable.

## 2026-06-14

- Added Skin aspect layout guards for detached windows, missing screens, and
  incomplete nib outlets.
- Added Skin preview and window guards instead of force unwrapping optional
  AppKit outlets and resize-window lifecycle state.

## 2026-06-13

- Replaced checked device-settings archive force unwrapping with device archive
  optional binding and the existing empty fallback.
- Added capture device switch rollback so rejected replacements restore the
  prior working input inside one session configuration transaction.

## 2026-06-12

- Made live capture-device settings construction nonfailable and removed its
  forced result unwrap while preserving failable archive decoding.
- Guarded `Skin` application-delegate lookup and made selection and settings
  coordination tolerate unavailable delegate lifecycle state.

## 2026-06-10

- Retained, replaced, and invalidated document aspect timers across preview and
  window teardown lifecycle events.
- Added a fixed macOS 15 GitHub Actions job that compiles the unsigned app and
  fixed the portable contract job to Ubuntu 24.04.
- Updated the Xcode project from unsupported Swift 2.3 language mode and macOS
  10.9 deployment metadata to Swift 5 and macOS 10.13.
- Migrated notification observation, device archive coding, application access,
  retry counting, and mouse event overrides to Swift 5 syntax.
- Migrated keyed archives, AVFoundation identifiers, AppKit window APIs,
  numeric formatting, and CoreMediaIO buffer sizing to current SDK names.
- Fixed Swift 5 call labels and value-type initializer delegation exposed by
  the hosted Xcode type checker.
- Migrated the capture skin's AppKit, AVFoundation, Core Animation, dispatch,
  notification, and input APIs to their Swift 5 forms.
- Migrated the document capture path to modern device discovery, input errors,
  timers, notifications, AppKit properties, and Core Animation constants.
- Made Makefile verification and build targets independent of the caller's
  working directory.
- Added a least-privilege GitHub Actions workflow that installs Python 3.12 and
  runs the static `make check` baseline with pinned Node 24-compatible actions
  and disabled checkout credential persistence.

## 2026-06-09

- Guarded device refreshes against missing main window outlet state before
  hiding or showing the device-list window.
- Guarded session window setup against missing main-screen and content-view
  state before adding the device skin.
- Guarded document preview setup and aspect updates against missing outlets,
  backing layers, input ports, and windows.
- Guarded capture input error presentation against missing `NSError` metadata
  and added static validation for the non-crashing path.
- Fixed the missing-settings fallback so it clears saved settings rather than
  the active capture-device list.
- Fixed `Document.updateAspect()` so video height changes are compared against
  the stored video height instead of being ignored by a self-comparison.
- Removed ad hoc `print`/`println` lifecycle logging from capture session and
  device connection observers.
- Removed skin-name debug logging and extended static behavior checks to reject
  active stdout app logging.

## 2026-06-08

- Removed local device-settings debug logging and added static validation to
  keep device names and saved window rectangles out of logs.
- Made device settings archive decoding fail closed instead of force-casting
  saved fields, with static checker coverage.
- Added `make check` as the shared repository verification alias.
- Guarded capture runtime-error observers against malformed notifications
  instead of force-unwrapping `userInfo` and `NSError` metadata.
- Extended the source checker to require safe runtime-error extraction and
  fallback logging in both app-level and document-level observers.
- Added a Makefile verification gate for shell syntax, Xcode project metadata,
  and capture permission metadata.
- Fixed `build.sh` so it is valid under its `/bin/sh` shebang.
- Added a camera usage description for connected-device mirroring permission
  prompts.
- Documented the local verification workflow.
- Added canonical `docs/plans` coverage and made project checks require
  completed plans.
