## ScreenShare Vision

ScreenShare is a macOS demo tool for mirroring a connected iOS device into a
clean, movable desktop window.

The repository is useful as a focused AVFoundation sample for discovering
screen-capture devices, starting a single device session, applying a device
skin, and handling connect/disconnect notifications.

The goal is to keep device mirroring reliable, explicit, and useful for live
demos without surprising capture or storage behavior.

The current focus is:

Priority:

- Preserve the connected-device mirroring flow
- Keep single-device limitations visible
- Handle capture runtime errors without crashing on malformed notifications
- Decode local device settings without force-cast launch crashes
- Keep saved device settings separate from active capture-device discovery
- Avoid logging local device names or saved window rectangles
- Avoid ad hoc stdout logging from app Swift sources
- Handle capture input setup failures without force-unwrapping error metadata
- Keep preview aspect updates responsive to width and height changes
- Maintain custom skin and screenshot context
- Keep completed maintenance plans under `docs/plans`
- Avoid recording, uploading, or storing mirrored content by default

Next priorities:

- Add setup notes for macOS, Xcode, and connected iOS devices
- Document permissions and device registration behavior
- Add manual verification notes for connect/disconnect handling
- Modernize Swift and project settings in a dedicated pass

Contribution rules:

- One PR = one focused device, session, UI, permission, or documentation change.
- Do not add capture persistence without explicit user controls.
- Include demo-device verification notes for behavior changes.
- Keep the demo workflow simple and visible.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Mirrored devices may show private apps, notifications, and customer data. The
tool should avoid hidden recording or uploads and should make capture windows
and permissions obvious during demos.

## What We Will Not Merge (For Now)

- Hidden recording or streaming
- Multi-device support without clear UI state
- Silent storage of mirrored frames
- Permission-bypass behavior
- Ad hoc stdout logging for capture lifecycle or device events

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
