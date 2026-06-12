# Changes

## 2026-06-10

- Added a GitHub Actions workflow that installs Python 3.12 and runs the static
  `make check` baseline for pushes and pull requests.

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
