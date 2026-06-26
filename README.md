# ScreenShare

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Device Preview

<!-- DEVICE-PREVIEW-IMAGE -->
![Device preview](docs/device-preview.svg)

## Overview

`garethpaul/ScreenShare` is an Apple platform application or Swift sample. ScreenShare is a great demo tool that allows you to mirror your iOS devices to your screen to create the perfect demo.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Swift (9), shell (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `build.sh`
- `CHANGES.md` - maintenance history for build and privacy checks
- `Makefile` - local verification entry points
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `scripts` - static project and behavior validators
- `ScreenShare` - source or example code
- `Screenshare.xcodeproj` - Xcode project file
- `ScreenShareTests` - source or example code
- `ScreenshareUITests` - source or example code
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: ScreenShare, ScreenShareTests, ScreenshareUITests
- Dependency and build manifests: none detected
- Entry points or build surfaces: build.sh, Screenshare.xcodeproj
- Test-looking files: ScreenShareTests/Info.plist, ScreenShareTests/ScreenShareTests.swift, ScreenshareUITests/Info.plist, ScreenshareUITests/ScreenshareUITests.swift

## Getting Started

### Supported macOS Baseline

- Git
- macOS with Xcode for building the AppKit application
- Python 3 for repository source checks
- Swift 5 with a macOS 10.13 deployment target, as pinned in the project
- An unlocked, trusted iPhone or iPad connected to the Mac over USB for live
  mirroring

### Setup

```bash
git clone https://github.com/garethpaul/ScreenShare.git
cd ScreenShare
open Screenshare.xcodeproj
```

Select the shared `Screenshare` scheme and the `My Mac` destination. Command-line
verification disables code signing; an interactive run may require a local
development team under the workstation's signing policy.

### Camera Permission Boundary

The app sandbox includes the sandbox camera entitlement. `Info.plist` declares
the exact usage text: `ScreenShare uses camera access to display connected iOS devices as demo capture sources.`
macOS may therefore ask for Camera permission. Denying that permission or
disabling it later prevents capture input from being admitted; ScreenShare does
not need Photos, microphone, screen-recording, network, or location permission.

### Connected iOS Device Registration

At launch, `DeviceUtils.registerForScreenCaptureDevices()` enables CoreMediaIO
property `kCMIOHardwarePropertyAllowScreenCaptureDevices`. The app then scans
AVFoundation muxed and video devices and admits connected hardware whose
model ID is `iOS Device`. Keep the iPhone or iPad unlocked, trust the Mac when
prompted by the device, and confirm macOS can see it before troubleshooting the
app.

### One-Device Session Limit

The current app supports one active mirrored device. If a second eligible
device appears while a session is active, ScreenShare presents `Only one device
supported` and asks the user to disconnect the other device. This is an
intentional admission boundary, not multi-device arbitration.

### Connect and Disconnect Behavior

ScreenShare observes `AVCaptureDevice.wasConnectedNotification` and
`AVCaptureDevice.wasDisconnectedNotification`, refreshes the device list on the
main queue, creates a window only after input and window attachment succeed,
and ends/closes a session when its device disappears. Reconnect and unlock the
device if it does not reappear; restart the app only after macOS itself sees the
device.

### Local Data Boundary

ScreenShare saves only local device identity/orientation/window geometry needed
to restore framing. It does not record mirrored video, upload frames, enumerate
user media, or persist a capture stream. Device names and saved rectangles are
excluded from debug logging by static contracts.

## Running or Using the Project

1. Open `Screenshare.xcodeproj` in Xcode.
2. Select the `Screenshare` scheme and `My Mac` destination.
3. Connect and unlock the iPhone or iPad that you want to mirror.
4. Run the app. ScreenShare scans for connected iOS capture devices and opens
   a phone or tablet frame when one is available.

Run `./build.sh` for the unsigned macOS unit-test gate. If no device window
appears, reconnect and unlock the device, confirm macOS can see it, and restart
the app. Signing is disabled for the command-line gate, but interactive Xcode
runs may still require a local development team depending on workstation policy.

## Testing and Verification

### Canonical Verification

Run:

```sh
/usr/bin/make check
```

- `make check` runs shell syntax checks, static Xcode project checks, and
  capture permission/runtime-error metadata checks. When `xcodebuild` is
  installed, the `build` target also builds the shared app scheme with code
  signing disabled.
- `./build.sh` runs the unsigned `Screenshare` unit-test scheme on macOS.
- `make test` runs the behavior checker plus hostile repository-copy mutations
  for initialization, preview, observer, geometry, pointer, and Xcode contracts.
- Static behavior checks also guard local device-settings archive decoding
  against force-cast crashes.
- Static behavior checks preserve device archive optional binding so decoded
  settings never require a force unwrap.
- Static behavior checks require live capture-device settings construction to
  be nonfailable and force-unwrap-free.
- Static behavior checks also reject debug logging of device names and saved
  window rectangles from local settings.
- Static behavior checks also keep missing local settings from clearing the
  active capture-device list.
- Static behavior checks also reject ad hoc `print`/`println` logging in app
  Swift sources while preserving explicit runtime-error diagnostics.
- Static behavior checks also ensure preview aspect updates compare both video
  width and height against the stored dimensions.
- Static behavior checks also require capture input setup failures to handle
  missing `NSError` metadata without force unwrapping.
- Static behavior checks require capture device switch rollback: replacement
  inputs are prepared and validated before a failed switch restores the prior
  working input.
- Skin capture device switch rollback preserves the prior working input when a
  replacement cannot be constructed or admitted.
- Initial Skin sessions reject unattached capture devices before window and
  view attachment.

### Hosted Native Verification

GitHub Actions runs the portable contract gate on Ubuntu 24.04 and builds the
unsigned `Screenshare` scheme on `macos-15`. Hosted build success proves source
and project compatibility; it does not prove a physical iOS device was trusted,
connected, authorized, mirrored, disconnected, and reconnected. Use the manual
steps above for that hardware boundary.
- Static behavior checks also require document preview setup and aspect updates
  to optional-bind outlets, backing layers, input ports, and windows.
- Skin preview and window guards optional-bind preview layers and resize-window
  lifecycle state instead of force unwrapping AppKit outlets.
- Skin owns an eager capture session and constructs one preview layer per loaded
  skin, avoiding nil-session initialization and duplicate preview rendering.
- Skin aspect layout guards tolerate detached windows, missing screens, and
  incomplete nib outlets during device-dimension updates, and reject non-finite
  or non-positive saved and computed geometry.
- Skin pointer and window guards keep drag and settings callbacks from
  force-unwrapping AppKit state during teardown, including hover callbacks.
- Device changes replace the observed format port instead of accumulating
  duplicate orientation callbacks across retries or switches.
- Static behavior checks also require session window setup to avoid
  force-unwrapping the main screen or content view.
- Session registration guards require window attachment to succeed before a
  capture skin is started or recorded as an active device session.
- Static behavior checks also require device refreshes to guard the main
  device-list window before hiding or showing it.
- Document aspect updates run once after session start and then only for the
  active input port's format-change notifications; device switches replace the
  observer and window teardown removes it.
- Static behavior checks also reject force-casting the application delegate and
  require skin selection/settings coordination to tolerate unavailable state.
- Static project checks also require completed canonical plans under `docs/plans`.
- GitHub Actions runs the static `make check` baseline on Ubuntu 24.04 and an
  unsigned app build on macOS 15, with pinned Node 24-compatible actions,
  read-only permissions, disabled checkout credential persistence, fixed runner
  images, and bounded timeouts.
- The shared Xcode project uses Swift 5 language mode and targets macOS 10.13
  or newer so current Xcode releases can compile it.
- Xcode's test action or `xcodebuild test` with the appropriate scheme and
  destination can be used on macOS for deeper verification. The unit-test
  target uses a distinct Swift module name to avoid colliding with the app.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include ScreenShare/AppDelegate.swift, ScreenShare/Document.swift, ScreenShare/NotificationManager.swift, ScreenShare/Skin.swift.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include ScreenShare/Info.plist, ScreenShareTests/Info.plist, ScreenshareUITests/Info.plist.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include ScreenShare/Skin.swift.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include ScreenShare/Info.plist, ScreenShare/Skin.swift, ScreenShareTests/Info.plist, ScreenshareUITests/Info.plist.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-screenshare-baseline.md` for the canonical
  mirroring privacy and runtime-error baseline.
- See `docs/plans/2026-06-08-device-archive-decoding.md` for the local
  device-settings archive guard.
- See `docs/plans/2026-06-08-device-settings-log-privacy.md` for the local
  device-settings logging guard.
- See `docs/plans/2026-06-09-stdout-logging-guard.md` for the app stdout
  logging guard.
- See `docs/plans/2026-06-09-video-height-change-detection.md` for the preview
  video height-change guard.
- See `docs/plans/2026-06-09-missing-settings-device-list.md` for the
  missing-settings device-list guard.
- See `docs/plans/2026-06-09-capture-input-error-guard.md` for the capture
  input error metadata guard.
- See `docs/plans/2026-06-13-device-switch-rollback.md` for capture device
  switch rollback and single-transaction session configuration.
- See `docs/plans/2026-06-13-device-archive-optional-binding.md` for the saved
  settings archive boundary.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for the
  caller-resistant, location-independent ScreenShare validation root.
- See `docs/plans/2026-06-21-make-authority-isolation.md` for checked-in recipe
  authority, hostile-input regression coverage, and the GNU Make preload and
  additional-`-f` startup boundary.
- See `docs/plans/2026-06-14-skin-preview-window-guards.md` for guarded Skin
  preview-layer and resize-window lifecycle setup.
- See `docs/plans/2026-06-09-document-preview-guard.md` for the document
  preview and aspect optional-binding guard.
- See `docs/plans/2026-06-09-session-window-setup-guard.md` for the session
  window setup guard.
- See `docs/plans/2026-06-09-main-window-refresh-guard.md` for the main
  device-list window refresh guard.
- See `docs/plans/2026-06-10-ci-baseline.md` for the GitHub Actions static
  baseline.
- See `docs/plans/2026-06-10-hosted-macos-build.md` for the hosted unsigned
  macOS build gate.
- See `docs/plans/2026-06-10-document-aspect-timer-teardown.md` for repeating
  preview timer lifecycle cleanup.
- See `docs/plans/2026-06-17-initial-skin-device-attachment-guard.md` for
  rejecting initial sessions that fail to attach their requested capture
  device.
- See `docs/plans/2026-06-19-screenshare-deep-review.md` for the consolidated
  initialization, preview, geometry, pointer, test-wrapper, and PR review.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
