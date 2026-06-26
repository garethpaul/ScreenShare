# Document Format Observer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Replace `Document`'s repeating aspect timer with active-port format-change notifications while preserving immediate initial layout and safe device switching.

**Architecture:** Reuse the repository's `NotificationManager` and the observer lifecycle already implemented by `Skin`. A dedicated manager owns exactly one active-port observer, replacement happens after each capture-session configuration transaction, and window teardown removes the observer.

**Tech Stack:** Swift 5, AppKit, AVFoundation, Python source-contract tests, XCTest/Xcode hosted build.

---

## Status: Completed

### Task 1: Define the observer contract

**Files:**
- Modify: `scripts/check-screenshare-source.py`
- Test: `scripts/test-screenshare-contracts.py`

**Step 1: Write the failing test**

Require `Document` to own a format-notification manager, replace the observer
after selected-input transactions, register the active port's
`formatDescriptionDidChangeNotification`, refresh once after session start,
and contain no repeating aspect timer.

**Step 2: Run test to verify it fails**

Run: `make test`

Expected: FAIL because `Document` still owns and schedules `aspectTimer` and
does not own an active-port observer.

### Task 2: Replace polling with notifications

**Files:**
- Modify: `ScreenShare/Document.swift`

**Step 1: Write minimal implementation**

Add `formatNotifications`, call `replaceFormatObserver()` after each selected
device transaction, register the current port with a weak main-queue callback,
call `updateAspect()` immediately after session start, and deregister the
format observer when the window closes.

**Step 2: Run test to verify it passes**

Run: `make test`

Expected: PASS.

### Task 3: Preserve mutation coverage and guidance

**Files:**
- Modify: `scripts/test-screenshare-contracts.py`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-26-document-format-observer.md`

**Step 1: Add hostile mutations**

Remove observer replacement and active-port registration independently and
verify the behavior contract rejects both repository copies.

**Step 2: Synchronize durable guidance**

Document that `Document` refreshes aspect state immediately and thereafter only
for the active port's format-change notifications.

**Step 3: Run complete verification**

Run: `make lint && make test && make build && make check`

Expected: all portable contracts pass; Xcode builds locally when available and
the hosted macOS job remains required on Linux.

**Step 4: Commit**

```bash
git add ScreenShare/Document.swift scripts/check-screenshare-source.py scripts/test-screenshare-contracts.py AGENTS.md README.md SECURITY.md VISION.md CHANGES.md docs/plans/2026-06-26-document-format-observer-design.md docs/plans/2026-06-26-document-format-observer.md
git commit -m "fix: observe document input format changes"
```

## Verification Completed

- The focused behavior contract failed against the repeating timer and missing
  active-port observer, then passed after the event-driven lifecycle landed.
- Two isolated hostile repository copies were rejected when observer
  replacement or notification registration was removed.
- A third hostile repository copy was rejected when synchronized public
  guidance was removed.
- `make check` and an external absolute-Make invocation passed 66 Make
  target/authority cases, project and behavior checks, and all 10 Python
  mutation tests.
- Local Xcode compilation skipped because `xcodebuild` is unavailable; the
  hosted unsigned macOS build remains required before merge.
