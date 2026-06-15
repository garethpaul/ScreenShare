# Changes

## 2026-06-15

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
