---
title: Reject Initial Skin Sessions Without a Capture Input
type: fix
date: 2026-06-17
---

# Reject Initial Skin Sessions Without a Capture Input

Status: In Progress

## Context

`Skin.selectedDevice` now preserves a working input when replacement
construction or admission fails. Initial session creation has no prior input,
however, and `AppDelegate.startNewSession` continues attaching, showing, and
registering the skin even when that first device assignment failed. The phantom
session has no capture input and blocks the connected-device retry path.

## Requirements

- R1. Verify the new skin is attached to the requested capture device before
  assigning its window or attaching its view.
- R2. End the failed skin session and return `nil` when initial input
  construction or admission leaves it unattached.
- R3. Keep notification registration, aspect setup, window presentation, and
  `deviceSessions` insertion limited to successfully attached skins.
- R4. Preserve the one-device policy and the existing transactional device
  switch rollback behavior.
- R5. Add mutation-sensitive static coverage for missing, inverted, late, or
  cleanup-free attachment guards.
- R6. Keep Linux validation portable and require the exact-head hosted macOS
  build for Apple-framework compilation evidence.

## Scope Boundaries

- Do not redesign `Skin.initWithDevice`, device discovery, or capture session
  ownership.
- Do not add dependencies or weaken the existing contract and hosted build
  gates.

## Implementation Units

### U1. Guard initial skin attachment

- **Goal:** Fail session creation before window/view side effects when the
  requested device did not become the skin's active input.
- **Files:** `ScreenShare/AppDelegate.swift`
- **Verification:** Source contract rejects missing, inverted, late, and
  cleanup-free guard mutations.

### U2. Make the startup boundary durable

- **Goal:** Register the guard in the portable checker and synchronize project
  guidance and evidence.
- **Files:** `scripts/check-screenshare-source.py`, `README.md`, `CHANGES.md`,
  `AGENTS.md`, `VISION.md`, `SECURITY.md`,
  `docs/plans/2026-06-17-initial-skin-device-attachment-guard.md`
- **Verification:** Repository and external-directory `make check`, explicit
  hostile mutations, and generated-artifact, recording-file, and credential
  audits.

## Verification

- Planned: focused project and behavior source contracts.
- Planned: hostile initial-attachment mutations.
- Planned: repository and external-directory `make check` on Linux.
- Planned: exact-head hosted macOS build.
