# Document Format Observer Design

## Status: Completed

## Current state

`Document.windowControllerDidLoadNib(_:)` starts a repeating one-second timer
that calls `updateAspect()`. The timer keeps aspect changes visible, but it also
wakes every second when the input format is unchanged. `Skin` already solves
the same lifecycle problem with a dedicated `NotificationManager` scoped to
the active input port.

Apple documents
`AVCaptureInput.Port.formatDescriptionDidChangeNotification` as the event sent
when a port's format description changes, with the changed port as the
notification object.

## Options considered

1. Keep polling, but only for muxed/iOS devices. This reduces some work while
   retaining a timer, device-type branching, and delayed updates.
2. Replace polling with the port-format notification. Refresh once immediately
   after session start, then react only when the active port changes format.
3. Keep a timer as a fallback behind the notification. This preserves redundant
   work and hides observer lifecycle defects instead of testing them.

## Decision

Use option 2 and mirror the existing `Skin` ownership pattern:

- give `Document` a separate format-notification manager;
- replace its observer after every selected-input transaction, including
  rollback or clearing;
- observe only the active input port and dispatch UI work to the main queue;
- perform one immediate aspect refresh after the capture session starts; and
- remove the obsolete timer and deregister the format observer at teardown.

This keeps initial layout deterministic, avoids stale-device callbacks after a
switch, and eliminates periodic work when the stream format is stable.

## Validation

- Add a source contract that fails while the repeating timer remains or the
  active-port observer lifecycle is absent.
- Add hostile repository-copy mutations for observer replacement and callback
  registration.
- Run all Make aliases and the hosted unsigned macOS build.

The implementation plan records the `make check` verification evidence.

## Evidence

- Apple documentation:
  <https://developer.apple.com/documentation/AVFoundation/AVCaptureInput/Port/formatDescriptionDidChangeNotification>
- Existing repository precedent: `ScreenShare/Skin.swift` owns and replaces a
  dedicated format observer when its selected device changes.
