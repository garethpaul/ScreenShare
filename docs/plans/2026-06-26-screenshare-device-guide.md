# ScreenShare Device Setup Guide Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Document ScreenShare's supported macOS setup, camera permission, connected-iOS device registration, one-device limit, and connect/disconnect behavior from checked-in source.

**Architecture:** Preserve the Swift 5/macOS 10.13 app, CoreMediaIO opt-in, AVFoundation notifications, session logic, tests, workflow, and project settings. Add fail-closed contracts for setup and device-operation guidance, then retire only the three completed documentation roadmap items.

**Tech Stack:** Markdown, Python 3 static contracts, Swift 5/AppKit/AVFoundation/CoreMediaIO, GNU Make, Xcode, GitHub Actions

---

## Status: Completed

### Task 1: Add The Documentation Contract

**Files:**
- Modify: `scripts/check-screenshare-source.py`
- Test: `scripts/check-screenshare-source.py`

**Step 1: Write the failing test**

Require supported baseline, setup, permission, device registration, one-device, connect/disconnect, verification, roadmap, history, and completed-plan guidance.

**Step 2: Run test to verify it fails**

Run: `python3 scripts/check-screenshare-source.py --mode project`

Expected: FAIL because current guidance does not separate these operating boundaries.

### Task 2: Write The Device Guide

**Files:**
- Modify: `README.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`

**Step 1: Write minimal documentation**

Document Swift 5/macOS 10.13, Xcode project setup, sandbox camera entitlement and usage text, CoreMediaIO opt-in, unlocked/trusted USB device discovery, `iOS Device` filtering, one-session admission, automatic connect/disconnect refresh, local settings, and portable/native verification.

**Step 2: Run focused contracts**

Run: `python3 scripts/check-screenshare-source.py --mode project`

Expected: PASS.

### Task 3: Prove Drift Fails Closed

**Files:**
- Test: `scripts/check-screenshare-source.py`

**Step 1: Apply hostile mutations**

Mutate project versions, permission, registration, device identity, one-device limit, connect/disconnect behavior, local-data boundary, verification, roadmap, history, and plan status.

**Step 2: Verify each mutation fails**

Run the project checker after each mutation.

Expected: every mutation is rejected.

### Task 4: Run The Full Gate

**Files:**
- Verify: `Makefile`

**Step 1: Run repository and external gates**

Run: `/usr/bin/make check`

Run: `cd "$(mktemp -d)" && /usr/bin/make -f /absolute/path/to/Makefile check`

Expected: portable project/behavior/mutation/Make authority gates pass; hosted macOS supplies the unsigned native build.

### Task 5: Commit And Ship

**Files:**
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-26-screenshare-device-guide.md`

**Step 1: Record exact validation**

Add mutation, local gate, hosted build, review, and blocker evidence.

**Step 2: Commit**

```bash
git add README.md VISION.md CHANGES.md scripts/check-screenshare-source.py docs/plans/2026-06-26-screenshare-device-guide.md
git commit -m "docs: document ScreenShare device setup"
```

## Results

- The focused project checker passed after the expected documentation-contract
  failure and the guide update.
- All 19 isolated hostile documentation mutations were rejected.
- `/usr/bin/make check` passed from the checkout and an unrelated working
  directory, including 66 Make target/authority cases and seven Python contract
  tests per invocation.
- Source claims were audited against the entitlement and usage plists, Swift
  lifecycle code, Xcode settings, and the pinned Ubuntu/macOS workflow.
- Live trust, authorization, mirroring, disconnect, and reconnect verification
  remains a physical-device boundary.
