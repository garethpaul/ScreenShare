# ScreenShare Deep Review Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Consolidate PRs #7-#18 while fixing the remaining capture initialization, preview, geometry, and pointer lifecycle defects with mutation-sensitive evidence.

**Architecture:** Keep the existing legacy AppKit/AVFoundation structure and strengthen invariants at their ownership boundaries. `Skin` owns an always-valid capture session and one preview layer, geometry helpers reject unusable persisted or computed sizes, and pointer handlers tolerate unavailable outlets. The Python contract gate gains isolated hostile mutations so these invariants cannot be removed without a failing test.

**Tech Stack:** Swift 5/AppKit/AVFoundation, Python 3 contract tests, POSIX shell, GNU Make, Xcode/macOS build validation, GitHub Actions.

Status: Completed

---

### Task 1: Add mutation-sensitive contract tests

**Files:**
- Create: `scripts/test-screenshare-contracts.py`
- Modify: `Makefile`

**Step 1: Write failing mutations**

Add isolated repository-copy tests that remove eager `Skin` session initialization, restore duplicate preview setup, remove finite geometry validation, and restore pointer outlet force dereferences.

**Step 2: Verify RED**

Run: `python3 scripts/test-screenshare-contracts.py`

Expected: FAIL because the current checker accepts at least one hostile mutation.

### Task 2: Make Skin initialization and preview ownership safe

**Files:**
- Modify: `ScreenShare/Skin.swift`
- Modify: `scripts/check-screenshare-source.py`

**Step 1: Add source contracts**

Require an eagerly initialized capture session and exactly one preview-layer construction path.

**Step 2: Implement minimal fix**

Initialize `session` at property construction and remove duplicate preview-layer creation from `initWithDevice`.

**Step 3: Verify GREEN**

Run: `python3 scripts/test-screenshare-contracts.py`

Expected: initialization and duplicate-preview mutations are rejected.

### Task 3: Reject unusable aspect geometry

**Files:**
- Modify: `ScreenShare/Extensions.swift`
- Modify: `ScreenShare/Device.swift`
- Modify: `ScreenShare/Skin.swift`
- Modify: `scripts/check-screenshare-source.py`

**Step 1: Add finite geometry contracts**

Require positive finite sizes before scaling or applying saved window rectangles.

**Step 2: Implement minimal fix**

Add reusable finite-positive size and usable-window-rectangle predicates, use them for archived settings and layout entry points, and fail closed with controlled diagnostics.

**Step 3: Verify GREEN**

Run: `python3 scripts/test-screenshare-contracts.py`

Expected: geometry mutations are rejected and baseline behavior checks pass.

### Task 4: Guard pointer outlet lifecycle

**Files:**
- Modify: `ScreenShare/Skin.swift`
- Modify: `scripts/check-screenshare-source.py`

**Step 1: Add pointer mutations**

Require `mouseEntered` and `mouseExited` to optional-bind the resize handle.

**Step 2: Implement minimal fix**

Return with a controlled diagnostic when the resize-handle outlet is unavailable.

**Step 3: Verify GREEN**

Run: `python3 scripts/test-screenshare-contracts.py`

Expected: pointer mutations are rejected.

### Task 5: Reconcile documentation PR #7

**Files:**
- Modify: `README.md`
- Modify: `build.sh` only if the lifecycle stack does not already contain the POSIX function syntax change

**Step 1: Integrate non-duplicated run guidance**

Preserve the current supported Xcode/macOS build guidance while incorporating useful device prerequisites and troubleshooting from PR #7.

**Step 2: Verify docs and shell contracts**

Run: `sh -n build.sh && make lint`

Expected: PASS.

### Task 6: Complete local and hosted validation

**Files:**
- Modify: `CHANGES.md`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `docs/plans/2026-06-19-screenshare-deep-review.md`

**Step 1: Run local gates**

Run: `python3 scripts/test-screenshare-contracts.py`, `make check`, an external-directory `make -f ... check`, `git diff --check`, and credential/generated-artifact scans.

Expected: PASS, including an unsigned native macOS build when Xcode is available.

**Step 2: Record completed evidence**

Update this plan to `Status: Completed` with exact commands and residual device/toolchain risks.

**Step 3: Commit and push aggregate head**

Create a focused remediation commit on top of PR #18, push an aggregate branch, and open a PR against `master`.

**Step 4: Run hosted gates and land**

Wait for required checks, merge without bypassing branch protection, then close or allow GitHub to mark PRs #7-#18 merged/superseded according to ancestry.

## Verification Evidence

- Seven red-first hostile repository-copy mutations cover eager session setup,
  duplicate preview layers, format-observer replacement, saved geometry,
  pointer hover outlets, test-module isolation, and current XCTest APIs.
- `./build.sh` passed two unsigned native unit tests on Xcode 26.0.1 after the
  test module and XCTest fixes.
- `make check` and an external-directory `make -f ... check` passed, including
  static contracts, mutation tests, and the unsigned macOS app build.
- `git diff --check`, shell syntax validation, no-new-generated-artifact scans,
  and high-signal credential-pattern scans passed. The unchanged tracked asset
  `ScreenShare/Images.xcassets/.DS_Store` predates this review.
- Hosted pull-request and post-merge results are recorded in the final review
  outcome for this plan.

## Residual Risk

- No physical iPhone or iPad was connected, so live device discovery, USB
  capture, format-change delivery, orientation changes, disconnect handling,
  window movement, and pointer resizing were not exercised end to end.
- The app and unit tests compile and run on current Xcode, but historical macOS
  10.13 behavior and older hardware remain unverified.
