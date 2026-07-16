#!/usr/bin/env python3
import argparse
import plistlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-screenshare-baseline.md"
DOCUMENT_PREVIEW_PLAN = DOCS_PLANS / "2026-06-09-document-preview-guard.md"
CI_PLAN = DOCS_PLANS / "2026-06-10-ci-baseline.md"
DEVICE_SWITCH_ROLLBACK_PLAN = DOCS_PLANS / "2026-06-13-device-switch-rollback.md"
DEVICE_ARCHIVE_BINDING_PLAN = DOCS_PLANS / "2026-06-13-device-archive-optional-binding.md"
MAKE_ROOT_PLAN = DOCS_PLANS / "2026-06-14-make-root-override-protection.md"
MAKE_AUTHORITY_PLAN = DOCS_PLANS / "2026-06-21-make-authority-isolation.md"
SKIN_PREVIEW_WINDOW_PLAN = DOCS_PLANS / "2026-06-14-skin-preview-window-guards.md"
SKIN_ASPECT_LAYOUT_PLAN = DOCS_PLANS / "2026-06-14-skin-aspect-layout-guards.md"
SKIN_POINTER_WINDOW_PLAN = DOCS_PLANS / "2026-06-15-skin-pointer-window-guards.md"
SESSION_REGISTRATION_PLAN = DOCS_PLANS / "2026-06-15-session-registration-guard.md"
SKIN_DEVICE_SWITCH_PLAN = DOCS_PLANS / "2026-06-16-skin-device-switch-rollback.md"
INITIAL_SKIN_ATTACHMENT_PLAN = DOCS_PLANS / "2026-06-17-initial-skin-device-attachment-guard.md"
DEVICE_GUIDE_PLAN = DOCS_PLANS / "2026-06-26-screenshare-device-guide.md"
EXPECTED_WORKFLOW = """name: Check

on:
  pull_request:
  push:
    branches:
      - master
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  contract:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: "3.12"

      - name: Run static contract
        run: make check

  build:
    runs-on: macos-15
    timeout-minutes: 15
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false

      - name: Show Xcode version
        run: /usr/bin/xcodebuild -version

      - name: Build unsigned macOS app
        run: make build
"""


# Ported verbatim from ios-app-share's check-baseline.py, the working reference in
# this account: a real scanner handling nested /* */ blocks, string-aware and
# escape-aware. A naive //[^\n]* regex would blank the rest of the line for
# `let u = "https://example.com"` and fail a contract against correct source.
#
# Every "must contain" assertion below read Swift raw, so a commented-out call
# satisfied its own assertion while the code was dead. Verified: block-commenting
# formatNotifications.deregisterAll() inside replaceFormatObserver() left
# `make check` at exit 0 -- the literal count in Skin.swift stayed at 2 while live
# occurrences dropped to 1 -- reintroducing the accumulating-callback bug the gate
# exists to prevent. Deleting the same call IS caught ("Skin device changes must
# replace the format observer instead of accumulating callbacks"), so the gate was
# live but blind.
#
# Note the pre-existing asymmetry this closes: the print/println scan below already
# skips comment lines, because there a comment would cause a false POSITIVE. The
# same awareness was absent from the "must contain" checks, where a comment causes
# false ASSURANCE.
def strip_swift_comments(text):
    result = []
    index = 0
    block_depth = 0
    in_string = False
    escaped = False

    while index < len(text):
        character = text[index]
        next_character = text[index + 1] if index + 1 < len(text) else ""

        if block_depth:
            if character == "/" and next_character == "*":
                block_depth += 1
                index += 2
                continue
            if character == "*" and next_character == "/":
                block_depth -= 1
                index += 2
                continue
            if character == "\n":
                result.append(character)
            index += 1
            continue

        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue

        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == "/" and next_character == "/":
            newline = text.find("\n", index + 2)
            if newline == -1:
                break
            result.append("\n")
            index = newline + 1
            continue
        if character == "/" and next_character == "*":
            block_depth = 1
            index += 2
            continue

        result.append(character)
        index += 1

    return "".join(result)


def read_text(relative_path):
    """Read a file, blanking Swift comments so assertions see live code only.

    Non-Swift files (README, plists, project files) are returned untouched.
    """
    text = (ROOT / relative_path).read_text(encoding="utf-8")
    if str(relative_path).endswith(".swift"):
        return strip_swift_comments(text)
    return text


def read_text_raw(relative_path):
    """Read a file untouched, comments included.

    Only for assertions genuinely ABOUT comment text. Code assertions must use
    read_text(), or a commented-out call satisfies its own assertion.
    """
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_plist(relative_path):
    return plistlib.loads((ROOT / relative_path).read_bytes())


def require_paths():
    errors = []
    for relative_path in (
        "build.sh",
        ".github/workflows/check.yml",
        "Screenshare.xcodeproj/project.pbxproj",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/Screenshare.xcscheme",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUnitTests.xcscheme",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUITests.xcscheme",
        "ScreenShare/Info.plist",
        "ScreenShare/Screenshare.entitlements",
        "ScreenShare/AppDelegate.swift",
        "ScreenShare/Document.swift",
        "ScreenShare/Device.swift",
        "ScreenShare/Skin.swift",
    ):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")
    return errors


def docs_plan_checks():
    errors = []
    normalized_readme = " ".join(read_text("README.md").split())
    for contract in (
        "Supported macOS Baseline",
        "Swift 5 with a macOS 10.13 deployment target",
        "Camera Permission Boundary",
        "sandbox camera entitlement",
        "ScreenShare uses camera access to display connected iOS devices as demo capture sources.",
        "Connected iOS Device Registration",
        "kCMIOHardwarePropertyAllowScreenCaptureDevices",
        "model ID is `iOS Device`",
        "One-Device Session Limit",
        "Connect and Disconnect Behavior",
        "AVCaptureDevice.wasConnectedNotification",
        "AVCaptureDevice.wasDisconnectedNotification",
        "Local Data Boundary",
        "Canonical Verification",
        "/usr/bin/make check",
        "Hosted Native Verification",
    ):
        if contract not in normalized_readme:
            errors.append(f"README device guide must preserve: {contract}")
    normalized_vision = " ".join(read_text("VISION.md").split())
    normalized_changes = " ".join(read_text("CHANGES.md").split())
    if "Keep macOS setup, camera permission, device registration, and connect/disconnect guidance synchronized with source" not in normalized_vision:
        errors.append("VISION must preserve the ScreenShare device-guide boundary")
    if "Completed three ScreenShare device-documentation priorities" not in normalized_changes:
        errors.append("CHANGES must record the ScreenShare device-guide reconciliation")
    if not DEVICE_GUIDE_PLAN.exists():
        errors.append("ScreenShare device guide plan is missing")
    else:
        plan = DEVICE_GUIDE_PLAN.read_text(encoding="utf-8")
        if "## Status: Completed" not in plan or "Document ScreenShare's supported macOS setup" not in plan:
            errors.append("ScreenShare device guide plan must record completed evidence")
    if not CANONICAL_PLAN.exists():
        errors.append("docs/plans/2026-06-08-screenshare-baseline.md is missing")
    if not DOCUMENT_PREVIEW_PLAN.exists():
        errors.append("docs/plans/2026-06-09-document-preview-guard.md is missing")
    if not CI_PLAN.exists():
        errors.append("docs/plans/2026-06-10-ci-baseline.md is missing")
    if not DEVICE_SWITCH_ROLLBACK_PLAN.exists():
        errors.append("docs/plans/2026-06-13-device-switch-rollback.md is missing")
    if not DEVICE_ARCHIVE_BINDING_PLAN.exists():
        errors.append("docs/plans/2026-06-13-device-archive-optional-binding.md is missing")
    if not MAKE_ROOT_PLAN.exists():
        errors.append("docs/plans/2026-06-14-make-root-override-protection.md is missing")
    if not MAKE_AUTHORITY_PLAN.exists():
        errors.append("docs/plans/2026-06-21-make-authority-isolation.md is missing")
    if not SKIN_PREVIEW_WINDOW_PLAN.exists():
        errors.append("docs/plans/2026-06-14-skin-preview-window-guards.md is missing")
    if not SKIN_ASPECT_LAYOUT_PLAN.exists():
        errors.append("docs/plans/2026-06-14-skin-aspect-layout-guards.md is missing")
    if not SKIN_POINTER_WINDOW_PLAN.exists():
        errors.append("docs/plans/2026-06-15-skin-pointer-window-guards.md is missing")
    if not SESSION_REGISTRATION_PLAN.exists():
        errors.append("docs/plans/2026-06-15-session-registration-guard.md is missing")
    if not SKIN_DEVICE_SWITCH_PLAN.exists():
        errors.append("docs/plans/2026-06-16-skin-device-switch-rollback.md is missing")
    if not INITIAL_SKIN_ATTACHMENT_PLAN.exists():
        errors.append("docs/plans/2026-06-17-initial-skin-device-attachment-guard.md is missing")

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    if not plans:
        errors.append("docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        if "Status: Completed" not in plan or "make check" not in plan:
            errors.append(f"{plan_path.relative_to(ROOT)} must record completed status and make check verification")

    return errors


def project_checks():
    errors = docs_plan_checks() + require_paths()
    if errors:
        return errors

    build_script = read_text("build.sh")
    if not build_script.startswith("#!/bin/sh"):
        errors.append("build.sh must keep its /bin/sh shebang")
    if re.search(r"\bfunction\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", build_script):
        errors.append("build.sh must use POSIX shell function syntax")
    for fragment in (
        "/usr/bin/xcodebuild -project Screenshare.xcodeproj",
        '-scheme "Screenshare"',
        '-destination "platform=macOS"',
        "CODE_SIGNING_ALLOWED=NO",
        "test",
    ):
        if fragment not in build_script:
            errors.append(f"build.sh is missing expected xcodebuild fragment: {fragment}")

    project_file = read_text("Screenshare.xcodeproj/project.pbxproj")
    if project_file.count("PRODUCT_MODULE_NAME = ScreenshareUnitTests;") != 2:
        errors.append("Unit test module name must not collide with the app module")
    unit_tests = read_text("ScreenShareTests/ScreenShareTests.swift")
    if "measureBlock" in unit_tests or "self.measure {" not in unit_tests:
        errors.append("Unit tests must use the current XCTest measure API")

    workflow = read_text(".github/workflows/check.yml")
    if workflow != EXPECTED_WORKFLOW:
        errors.append("GitHub Actions workflow must match the reviewed credential-free contract and macOS build baseline")

    makefile = read_text("Makefile")
    root_declaration = "override ROOT := $(shell path='$(subst ','\"'\"',$(MAKEFILE_LIST))'; path=$$(printf '%s' \"$$path\" | /usr/bin/sed 's/^ //'); [ -f \"$$path\" ] || exit 1; directory=$$(/usr/bin/dirname -- \"$$path\"); CDPATH= cd -- \"$$directory\" && /bin/pwd -P)"
    root_assignments = [
        line
        for line in makefile.splitlines()
        if re.match(r"^(?:override\s+)?ROOT\s*[:?+]?=", line)
    ]
    if root_assignments != [root_declaration]:
        errors.append("Makefile must define exactly one safe repository-derived ROOT declaration")
    for fragment in (
        ".DEFAULT_GOAL := check",
        "override SHELL := /bin/sh",
        "override .SHELLFLAGS := -c",
        "override PYTHON := $(ROOT)/scripts/run-python.sh",
        "override XCODEBUILD := $(ROOT)/scripts/run-xcodebuild.sh",
        "export PYTHON XCODEBUILD",
        "override PYTHONDONTWRITEBYTECODE := 1",
        "export PYTHONDONTWRITEBYTECODE",
        "$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)",
        "override MAKEFILES :=",
        "$(error MAKEFILE_LIST must not be overridden)",
        root_declaration,
        "export ROOT",
        "$(error repository Makefile path could not be resolved)",
        '\t/bin/sh -n "$$ROOT/build.sh"',
        '"$$PYTHON" "$$ROOT/scripts/check-screenshare-source.py" --mode project',
        '"$$PYTHON" "$$ROOT/scripts/test-screenshare-contracts.py"',
        'cd "$$ROOT" && "$$XCODEBUILD" -project Screenshare.xcodeproj',
        "CODE_SIGNING_ALLOWED=NO build",
        "root-test:",
        '\t/bin/sh "$$ROOT/scripts/test-makefile-root.sh"',
        "verify: root-test lint test build",
    ):
        if fragment not in makefile:
            errors.append(f"Makefile is missing root-independent fragment: {fragment}")

    expected_launchers = {
        "scripts/run-python.sh": "exec /usr/bin/python3 -I -B -c",
        "scripts/run-xcodebuild.sh": 'exec /usr/bin/xcodebuild "$@"',
    }
    for relative_path, fragment in expected_launchers.items():
        launcher = read_text(relative_path)
        if fragment not in launcher:
            errors.append(f"{relative_path} must use the trusted absolute tool launcher")

    mutation_tests = read_text("scripts/test-screenshare-contracts.py")
    if 'str(repository / "scripts/run-python.sh")' not in mutation_tests:
        errors.append("contract mutation tests must use the isolated repository Python launcher")

    if MAKE_ROOT_PLAN.exists():
        root_plan = MAKE_ROOT_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "`make ROOT=/tmp check` passed",
            "all five public Make aliases passed",
            "Six hostile mutations were rejected",
            "Python 3.12",
        ):
            if evidence not in root_plan:
                errors.append(
                    f"{MAKE_ROOT_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}"
                )
        if str(MAKE_ROOT_PLAN.relative_to(ROOT)) not in read_text("README.md"):
            errors.append(f"README.md must reference {MAKE_ROOT_PLAN.relative_to(ROOT)}")

    root_test = ROOT / "scripts" / "test-makefile-root.sh"
    if root_test.exists():
        root_test_text = root_test.read_text(encoding="utf-8")
        for evidence in (
            "66 executed target/authority cases",
            "MAKEFILE_LIST must not be overridden",
            "3 documented GNU Make startup-boundary cases",
            "later-startup-ran",
        ):
            if evidence not in root_test_text:
                errors.append(f"{root_test.relative_to(ROOT)} must preserve {evidence!r}")
    else:
        errors.append("scripts/test-makefile-root.sh is missing")

    if MAKE_AUTHORITY_PLAN.exists():
        authority_plan = MAKE_AUTHORITY_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "`make root-test` passed 66 target/authority cases, two metadata rejection",
            "checked-in Makefile cannot make an already-started GNU Make process safe",
            "`make check` passed from the repository and through an absolute Makefile path",
        ):
            if evidence not in authority_plan:
                errors.append(
                    f"{MAKE_AUTHORITY_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}"
                )
        if str(MAKE_AUTHORITY_PLAN.relative_to(ROOT)) not in read_text("README.md"):
            errors.append(f"README.md must reference {MAKE_AUTHORITY_PLAN.relative_to(ROOT)}")

    for doc_path in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
        document = re.sub(r"\s+", " ", read_text(doc_path))
        if "GitHub Actions" not in document:
            errors.append(f"{doc_path} must document the GitHub Actions baseline")
        if "capture device switch rollback" not in document.lower():
            errors.append(f"{doc_path} must document capture device switch rollback")
        if "skin capture device switch rollback preserves the prior working input" not in document.lower():
            errors.append(f"{doc_path} must document Skin device switch rollback")
        if "device archive optional binding" not in document.lower():
            errors.append(f"{doc_path} must document device archive optional binding")
        if "skin preview and window guards" not in document.lower():
            errors.append(f"{doc_path} must document Skin preview and window guards")
        if "skin aspect layout guards" not in document.lower():
            errors.append(f"{doc_path} must document Skin aspect layout guards")
        if "skin pointer and window guards" not in document.lower():
            errors.append(f"{doc_path} must document Skin pointer and window guards")
        if "initial skin sessions reject unattached capture devices before window and view attachment" not in document.lower():
            errors.append(f"{doc_path} must document initial Skin attachment rejection")
        if "document aspect updates run once after session start and then only for the active input port's format-change notifications" not in document.lower():
            errors.append(f"{doc_path} must document event-driven Document aspect updates")
        if "document and skin select the explicit video port instead of relying on capture input port ordering" not in document.lower():
            errors.append(f"{doc_path} must document explicit video-port selection")
    if str(SKIN_PREVIEW_WINDOW_PLAN.relative_to(ROOT)) not in read_text("README.md"):
        errors.append(f"README.md must reference {SKIN_PREVIEW_WINDOW_PLAN.relative_to(ROOT)}")
    if "Skin capture device switch rollback preserves the prior working input" not in read_text("AGENTS.md"):
        errors.append("AGENTS.md must document Skin device switch rollback")
    agents = re.sub(r"\s+", " ", read_text("AGENTS.md"))
    if "Initial Skin sessions reject unattached capture devices before window and view attachment" not in agents:
        errors.append("AGENTS.md must document initial Skin attachment rejection")
    if "Document aspect updates run once after session start and then only for the active input port's format-change notifications" not in agents:
        errors.append("AGENTS.md must document event-driven Document aspect updates")
    if "Document and Skin select the explicit video port instead of relying on capture input port ordering" not in agents:
        errors.append("AGENTS.md must document explicit video-port selection")

    project = read_text("Screenshare.xcodeproj/project.pbxproj")
    for fragment in (
        "ScreenShareTests",
        "ScreenshareUITests",
        'CODE_SIGN_ENTITLEMENTS = "$(PROJECT_DIR)/ScreenShare/Screenshare.entitlements";',
        "MACOSX_DEPLOYMENT_TARGET = 10.13;",
        "SWIFT_VERSION = 5.0;",
    ):
        if fragment not in project:
            errors.append(f"project is missing expected setting: {fragment}")

    return errors


def behavior_checks():
    errors = require_paths()
    if errors:
        return errors

    app_delegate = read_text("ScreenShare/AppDelegate.swift")
    document = read_text("ScreenShare/Document.swift")
    device = read_text("ScreenShare/Device.swift")
    extensions = read_text("ScreenShare/Extensions.swift")
    skin = read_text("ScreenShare/Skin.swift")
    if "AVCaptureDevice" not in app_delegate + skin:
        errors.append("app must keep AVFoundation device capture code visible")
    if "let session = AVCaptureSession()" not in skin or "var session : AVCaptureSession!" in skin:
        errors.append("Skin.session must be initialized before nib-backed preview setup")
    if skin.count("let videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)") != 1:
        errors.append("Skin must construct exactly one capture preview layer")
    format_observer_start = skin.find("private func replaceFormatObserver()")
    format_observer_end = skin.find("func getVideoDimensions()", format_observer_start)
    format_observer = skin[format_observer_start:format_observer_end]
    # Pin the whole construct, not the bare call: asserting only that the literal appears
    # somewhere in the method cannot tell a live deregister from a dead one. Wrapping the
    # call in `if false { ... }` keeps the literal present and uncommented while observers
    # accumulate again. Requiring the call to BE the first statement rejects that, using
    # the same contiguous-literal form as archive_binding below.
    deregister_first = (
        "private func replaceFormatObserver() {\n"
        "        formatNotifications.deregisterAll()\n"
    )
    if (
        format_observer_start < 0
        or format_observer_end < 0
        or deregister_first not in format_observer
        or "forObject: port" not in format_observer
    ):
        errors.append("Skin device changes must replace the format observer instead of accumulating callbacks")

    entitlements = read_plist("ScreenShare/Screenshare.entitlements")
    if entitlements.get("com.apple.security.device.camera") is not True:
        errors.append("camera entitlement must remain enabled for capture devices")

    info = read_plist("ScreenShare/Info.plist")
    camera_reason = info.get("NSCameraUsageDescription", "").strip()
    if not camera_reason:
        errors.append("Info.plist must explain camera access with NSCameraUsageDescription")
    elif "connected iOS devices" not in camera_reason:
        errors.append("NSCameraUsageDescription must mention connected iOS devices")

    runtime_sources = app_delegate + document
    if "userInfo!" in runtime_sources:
        errors.append("runtime-error observers must not force unwrap notification userInfo")
    if "AVCaptureSessionErrorKey] as! NSError" in runtime_sources:
        errors.append("runtime-error observers must not force cast capture errors")
    safe_error_extractions = runtime_sources.count("note.userInfo?[AVCaptureSessionErrorKey] as? NSError")
    if safe_error_extractions < 2:
        errors.append("both runtime-error observers must optional-bind AVCaptureSessionErrorKey as NSError")
    if runtime_sources.count("Capture session runtime error notification missing NSError metadata") < 2:
        errors.append("runtime-error observers must log malformed capture error notifications")
    if "self.devices = []" in app_delegate:
        errors.append("AppDelegate.loadDeviceSettings must not clear active capture devices when settings are missing")
    if "self.deviceSettings = []" not in app_delegate:
        errors.append("AppDelegate.loadDeviceSettings must reset saved device settings when no archive exists")
    if "loaded!" in app_delegate:
        errors.append("AppDelegate.loadDeviceSettings must not force unwrap decoded device settings")
    archive_binding = (
        "if let loaded = NSKeyedUnarchiver.unarchiveObject(withFile: Device.ArchivePath) as? [Device] {\n"
        "            self.deviceSettings = loaded\n"
        "        } else {\n"
        "            self.deviceSettings = []\n"
        "        }"
    )
    if archive_binding not in app_delegate:
        errors.append("AppDelegate.loadDeviceSettings must optional-bind the archive and fail closed to empty saved settings")
    if re.search(r"decodeObject(?:ForKey|\(forKey:)\s*\(?PropertyKey\.nameKey\)?\s+as!\s+String", device):
        errors.append("Device archive decoding must not force-cast saved settings")
    if "guard let name = aDecoder.decodeObject(forKey: PropertyKey.nameKey) as? String" not in device:
        errors.append("Device archive decoding must optional-bind saved settings fields")
    if "required convenience init?(coder aDecoder: NSCoder)" not in device:
        errors.append("Device archive decoding must remain failable for malformed saved settings")
    if "return savedSettingForOrientation(forOrientation: forOrientation).hasUsableWindowGeometry" not in device:
        errors.append("Device saved window geometry must reject non-finite or non-positive sizes")
    for fragment in (
        "var isFinitePositive: Bool",
        "width.isFinite && height.isFinite && width > 0 && height > 0",
        "var hasUsableWindowGeometry: Bool",
        "origin.x.isFinite && origin.y.isFinite && size.isFinitePositive",
    ):
        if fragment not in extensions:
            errors.append(f"ScreenShare geometry helpers must retain finite-positive validation via {fragment!r}")
    if "convenience init?(fromDevice device: AVCaptureDevice)" in device:
        errors.append("Live capture-device settings construction must not be failable")
    if "convenience init(fromDevice device: AVCaptureDevice)" not in device:
        errors.append("Device must expose nonfailable live capture-device settings construction")
    if "Device(fromDevice: device)!" in app_delegate:
        errors.append("AppDelegate must not force unwrap live device-settings construction")
    if "let newDevice = Device(fromDevice: device)\n        self.deviceSettings.append(newDevice)\n        return newDevice" not in app_delegate:
        errors.append("AppDelegate must append and return newly constructed device settings")
    if "dimensions.height != dimensions.height" in document:
        errors.append("Document.updateAspect must not compare dimensions.height to itself")
    if "dimensions.height != self.videoDimensions.height" not in document:
        errors.append("Document.updateAspect must compare new height to the stored video height")
    if "let err = error as NSError!" in document:
        errors.append("Document.displayError must not force unwrap optional NSError values")
    if "guard let error = error else" not in document:
        errors.append("Document.displayError must handle missing NSError metadata explicitly")
    if "Capture device input failed without NSError metadata" not in document:
        errors.append("Document.displayError must log missing capture input NSError metadata")
    if "previewViewLayer!" in document:
        errors.append("Document preview setup must not force unwrap the preview backing layer")
    if "guard let previewView = self.previewView" not in document:
        errors.append("Document preview setup must guard the preview outlet")
    if "guard let previewViewLayer = previewView.layer" not in document:
        errors.append("Document preview setup must guard the backing layer")
    if "let port = self.input?.ports.first as AVCaptureInputPort?" in document:
        errors.append("Document.updateAspect must not rely on a forced optional input-port cast")
    if "port!.formatDescription" in document:
        errors.append("Document.updateAspect must not force unwrap the input port")
    if "let windowFrame = window!.frame" in document:
        errors.append("Document.updateAspect must not force unwrap the document window")
    for fragment in (
        "extension AVCaptureDeviceInput",
        "var videoPort: AVCaptureInput.Port?",
        "ports.first { $0.mediaType == .video }",
    ):
        if fragment not in extensions:
            errors.append(f"capture inputs must select their video stream via {fragment!r}")
    if "self.input?.ports.first" in document or "self.input?.ports.first" in skin:
        errors.append("capture aspect handling must not rely on input-port ordering")
    if document.count("self.input?.videoPort") < 2:
        errors.append("Document must observe and measure the explicit video input port")
    if skin.count("self.input?.videoPort") < 2:
        errors.append("Skin must observe and measure the explicit video input port")
    if "guard let port = self.input?.videoPort" not in document:
        errors.append("Document.updateAspect must optional-bind the video capture input port")
    if "let window = self.windowForSheet" not in document:
        errors.append("Document.updateAspect must optional-bind the document window")
    if "private func resetResolutionStatus()" not in document:
        errors.append("Document.updateAspect must centralize resolution fallback state")
    if "let formatNotifications = NotificationManager()" not in document:
        errors.append("Document must own active-port format notifications separately")
    if "aspectTimer" in document or "Timer.scheduledTimer" in document:
        errors.append("Document must not poll for capture format changes")
    if "self.session.startRunning()\n        self.updateAspect()" not in document:
        errors.append("Document must refresh aspect state immediately after session start")
    if "self.session.commitConfiguration()\n                self.replaceFormatObserver()\n                self.updateAspect()" not in document:
        errors.append("Document device transactions must replace the active-port format observer")
    replace_format_start = document.find("private func replaceFormatObserver()")
    update_aspect_start = document.find("@objc func updateAspect()", replace_format_start)
    replace_format_observer = document[replace_format_start:update_aspect_start]
    for fragment in (
        "private func replaceFormatObserver()",
        "formatNotifications.deregisterAll()",
        "AVCaptureInput.Port.formatDescriptionDidChangeNotification",
        "forObject: port",
        "dispatchAsyncToMainQueue: true",
        "block: { [weak self] _ in",
        "self?.updateAspect()",
    ):
        if min(replace_format_start, update_aspect_start) < 0 or fragment not in replace_format_observer:
            errors.append(f"Document format observer must preserve {fragment!r}")
    if "formatNotifications.deregisterAll()\n        self.session.stopRunning()" not in document:
        errors.append("Document window teardown must release active-port format notifications")
    if re.search(r'print\("Using (Portrait|Landscape) settings', device):
        errors.append("Device saved settings must not log device names or saved window rectangles")
    if "NSLog(self.device.skin)" in skin:
        errors.append("Skin loading must not log selected skin names")
    if "NSApplication.shared.delegate as! AppDelegate" in skin:
        errors.append("Skin must not force-cast the application delegate")
    if "private var appDelegate: AppDelegate?" not in skin:
        errors.append("Skin must expose the application delegate as optional state")
    if "NSApplication.shared.delegate as? AppDelegate" not in skin:
        errors.append("Skin must conditionally cast the application delegate")
    if 'NSLog("ScreenShare application delegate is unavailable.")' not in skin:
        errors.append("Skin must log unavailable application delegate state")
    if "previewViewLayer!" in skin or "self.videoPreviewLayer!" in skin or "forObject: self.window!" in skin:
        errors.append("Skin preview and resize setup must not force unwrap optional AppKit state")
    if skin.count("guard let previewView = self.previewView") != 1 or skin.count("let previewViewLayer = previewView.layer") != 1:
        errors.append("Skin preview setup must guard its outlet and backing layer")
    if "originalPreviewViewBounds = previewView.bounds" not in skin:
        errors.append("Skin must retain preview bounds from the guarded local outlet")
    if "guard let window = self.window else" not in skin or "[weak self, weak window]" not in skin:
        errors.append("Skin resize notifications must guard and weakly retain window lifecycle state")
    resize_start = skin.find("func registerNotifications()")
    resize_end = skin.find("func initWithDevice(device: AVCaptureDevice)")
    resize_layout = skin[resize_start:resize_end]
    for fragment in (
        "let skinView = self.view,",
        "let deviceFrameImage = self.deviceFrameImage,",
        "let previewView = self.previewView else",
        "windowSize: window.frame.size,",
        "window: window,",
        "skinView: skinView,",
        "deviceFrameImage: deviceFrameImage,",
        "previewView: previewView)",
    ):
        if resize_start < 0 or resize_end < 0 or fragment not in resize_layout:
            errors.append(f"Skin resize layout must retain guarded state via {fragment!r}")
    if SKIN_PREVIEW_WINDOW_PLAN.exists():
        plan = SKIN_PREVIEW_WINDOW_PLAN.read_text(encoding="utf-8")
        for evidence in ("Status: Completed", "repository and external-directory `make check` passed", "hostile Skin optional-state mutations were rejected"):
            if evidence not in plan:
                errors.append(f"{SKIN_PREVIEW_WINDOW_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
    for fragment in (
        "guard let window = self.window,",
        "let skinView = self.view,",
        "let deviceFrameImage = self.deviceFrameImage,",
        "let previewView = self.previewView else",
        "let screen = window.screen ?? NSScreen.main",
        "var screenFrame = screen.visibleFrame",
        "positionWindow(windowRect: windowRect, window: window)",
        "centerWindow(windowSize: windowSize, window: window, screenFrame: screen.frame)",
        "func centerWindow(windowSize: NSSize, window: NSWindow, screenFrame: NSRect)",
        "func positionWindow(windowRect: NSRect, window: NSWindow)",
        "func updateViewsToWindow(windowSize: NSSize, window: NSWindow, skinView: NSView,",
        "window.invalidateShadow()",
    ):
        if fragment not in skin:
            errors.append(f"Skin aspect layout must retain guarded state via {fragment!r}")
    aspect_start = skin.find("func updateAspect(ignoreSettings:Bool)")
    aspect_end = skin.find("func scaleToFit(forgetSettings:Bool)")
    aspect_layout = skin[aspect_start:aspect_end]
    if aspect_start < 0 or aspect_end < 0 or "self.window!" in aspect_layout or "self.deviceSettings!" in aspect_layout:
        errors.append("Skin aspect layout must not force unwrap window or device settings state")
    if SKIN_ASPECT_LAYOUT_PLAN.exists():
        plan = SKIN_ASPECT_LAYOUT_PLAN.read_text(encoding="utf-8")
        for evidence in ("Status: Completed", "repository and external-directory `make check` passed", "hostile Skin aspect-layout mutations were rejected"):
            if evidence not in plan:
                errors.append(f"{SKIN_ASPECT_LAYOUT_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
    pointer_start = skin.find("override func mouseDown(with theEvent: NSEvent)")
    pointer_end = skin.find("override func viewDidEndLiveResize()")
    pointer_handlers = skin[pointer_start:pointer_end]
    for fragment in (
        "guard let window = self.window,",
        "let deviceFrameImage = self.deviceFrameImage else",
        "var pointerLocation = NSEvent.mouseLocation",
        "guard let initialLocation = initialLocation,",
        "let window = self.window else",
        "if let screenFrame = (window.screen ?? NSScreen.main)?.frame",
        "window.setFrameOrigin(newOrigin)",
    ):
        if pointer_start < 0 or pointer_end < 0 or fragment not in pointer_handlers:
            errors.append(f"Skin pointer handlers must retain guarded state via {fragment!r}")
    for unsafe_fragment in ("self.window!", "initialLocation!", "deviceFrameImage!", "screenFrame!"):
        if unsafe_fragment in pointer_handlers:
            errors.append(f"Skin pointer handlers must not force unwrap optional state via {unsafe_fragment!r}")
    settings_start = skin.find("func updateDeviceSettings()")
    settings_end = skin.find("func getDeviceSettings(device: AVCaptureDevice)")
    settings_update = skin[settings_start:settings_end]
    for fragment in (
        "guard let deviceSettings = self.deviceSettings,",
        "let window = self.window else",
        "deviceSettings.portraitRect = window.frame",
        "deviceSettings.landscapeRect = window.frame",
    ):
        if settings_start < 0 or settings_end < 0 or fragment not in settings_update:
            errors.append(f"Skin device settings persistence must retain guarded state via {fragment!r}")
    if "self.deviceSettings!" in settings_update or "window!" in settings_update:
        errors.append("Skin device settings persistence must not force unwrap optional state")
    if SKIN_POINTER_WINDOW_PLAN.exists():
        plan = SKIN_POINTER_WINDOW_PLAN.read_text(encoding="utf-8")
        for evidence in ("Status: Completed", "repository and external-directory `make check` passed", "hostile Skin pointer mutations were rejected"):
            if evidence not in plan:
                errors.append(f"{SKIN_POINTER_WINDOW_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
    for fragment in (
        "appDelegate?.selectedDevice = nil",
        "appDelegate?.selectedDevice = self",
        "appDelegate?.findDeviceSettings(device: device)",
        "appDelegate?.saveDeviceSettings()",
    ):
        if fragment not in skin:
            errors.append(f"Skin delegate interactions must tolerate missing delegate state: {fragment}")
    if "NSScreen.mainScreen()!.frame" in app_delegate or "NSScreen.main!.frame" in app_delegate:
        errors.append("AppDelegate.startNewSession must not force unwrap the main screen")
    if "let screenFrame = NSScreen.main?.frame ?? NSMakeRect" not in app_delegate:
        errors.append("AppDelegate.startNewSession must fall back when no main screen is available")
    if "window.contentView!" in app_delegate:
        errors.append("AppDelegate.startNewSession must not force unwrap the session window content view")
    if "guard let contentView = window.contentView else" not in app_delegate or "contentView.addSubview(skin)" not in app_delegate:
        errors.append("AppDelegate.startNewSession must guard the session window content view before adding the skin")
    session_start = app_delegate.find("func startNewSession(device:AVCaptureDevice)")
    session_end = app_delegate.find("func refreshDevices()", session_start)
    session_setup = app_delegate[session_start:session_end]
    for fragment in (
        "func startNewSession(device:AVCaptureDevice) -> Skin?",
        "guard let contentView = window.contentView else",
        "return nil",
        "let skin = Skin(frame: frameView)",
        "contentView.addSubview(skin)",
    ):
        if session_start < 0 or session_end < 0 or fragment not in session_setup:
            errors.append(f"AppDelegate session creation must retain failable setup via {fragment!r}")
    if session_setup.find("guard let contentView = window.contentView else") > session_setup.find("let skin = Skin(frame: frameView)"):
        errors.append("AppDelegate must guard the session window content view before constructing the capture skin")
    attachment_start = session_setup.find("guard skin.selectedDevice == device else")
    owner_assignment = session_setup.find("skin.ownerWindow = window")
    attachment_guard = session_setup[attachment_start:owner_assignment]
    if "skin.initWithDevice(device: device)" not in session_setup:
        errors.append("AppDelegate initial skin attachment must initialize the requested device")
    for fragment in (
        "guard skin.selectedDevice == device else",
        "skin.endSession()",
        "return nil",
    ):
        if attachment_start < 0 or owner_assignment < 0 or fragment not in attachment_guard:
            errors.append(f"AppDelegate initial skin attachment must retain guard via {fragment!r}")
    initialization = session_setup.find("skin.initWithDevice(device: device)")
    view_attachment = session_setup.find("contentView.addSubview(skin)")
    if min(initialization, attachment_start, owner_assignment, view_attachment) < 0 or not (
        initialization < attachment_start < owner_assignment < view_attachment
    ):
        errors.append("AppDelegate must validate initial capture input before window and view attachment")
    refresh_start = app_delegate.find("func refreshDevices()")
    refresh_setup = app_delegate[refresh_start:]
    if "if let skin = startNewSession(device: device)" not in refresh_setup:
        errors.append("AppDelegate must register only successfully created device sessions")
    if "self.deviceSessions[device] = startNewSession(device: device)" in refresh_setup:
        errors.append("AppDelegate must not register a failable device session unconditionally")
    if SESSION_REGISTRATION_PLAN.exists():
        plan = SESSION_REGISTRATION_PLAN.read_text(encoding="utf-8")
        for evidence in ("Status: Completed", "repository and external-directory `make check` passed", "hostile session-registration mutations were rejected"):
            if evidence not in plan:
                errors.append(f"{SESSION_REGISTRATION_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
    if SKIN_DEVICE_SWITCH_PLAN.exists():
        plan = SKIN_DEVICE_SWITCH_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "hostile Skin device-switch mutations were rejected",
            "generated-artifact and credential-pattern audits passed",
        ):
            if evidence not in plan:
                errors.append(f"{SKIN_DEVICE_SWITCH_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
    if INITIAL_SKIN_ATTACHMENT_PLAN.exists():
        plan = INITIAL_SKIN_ATTACHMENT_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "hostile initial Skin attachment mutations were rejected",
            "generated-artifact and credential-pattern audits passed",
        ):
            if evidence not in plan:
                errors.append(f"{INITIAL_SKIN_ATTACHMENT_PLAN.relative_to(ROOT)} must record verification evidence {evidence!r}")
        if str(INITIAL_SKIN_ATTACHMENT_PLAN.relative_to(ROOT)) not in read_text("README.md"):
            errors.append(f"README.md must reference {INITIAL_SKIN_ATTACHMENT_PLAN.relative_to(ROOT)}")
    if "self.window!.close()" in app_delegate or "self.window!.makeKeyAndOrderFront(NSApp)" in app_delegate:
        errors.append("AppDelegate.refreshDevices must not force unwrap the main device-list window")
    if "guard let window = self.window else" not in app_delegate:
        errors.append("AppDelegate.refreshDevices must guard the main device-list window outlet")
    if 'NSLog("Main device list window outlet is missing.")' not in app_delegate:
        errors.append("AppDelegate.refreshDevices must log a missing main window outlet")
    refresh_devices = re.search(r"func refreshDevices\(\)\s*\{(?P<body>.*?)^    \}", document, re.DOTALL | re.MULTILINE)
    if refresh_devices and "beginConfiguration()" in refresh_devices.group("body"):
        errors.append("Document.refreshDevices must not nest capture session configuration")
    if "let replacementInput: AVCaptureDeviceInput?" not in document or "replacementInput = try AVCaptureDeviceInput(device: newDevice)" not in document:
        errors.append("Document.selectedDevice must construct the replacement input before mutating the session")
    if "defer {\n                self.session.commitConfiguration()\n                self.replaceFormatObserver()\n                self.updateAspect()\n            }" not in document:
        errors.append("Document.selectedDevice must commit its transaction, replace the format observer, and refresh aspect state")
    if "guard self.session.canAddInput(replacementInput) else" not in document:
        errors.append("Document.selectedDevice must validate replacement input admission")
    if "self.session.canAddInput(previousInput)" not in document or "self.session.addInput(previousInput)\n                    self.input = previousInput" not in document:
        errors.append("Document.selectedDevice must restore the previous input when replacement admission fails")
    if 'NSLog("Capture session rejected the replacement device input.")' not in document:
        errors.append("Document.selectedDevice must log replacement rejection without device metadata")

    skin_switch_start = skin.find("var selectedDevice : AVCaptureDevice?")
    skin_switch_end = skin.find("func getVideoDimensions()", skin_switch_start)
    skin_switch = skin[skin_switch_start:skin_switch_end]
    for fragment in (
        "let replacementInput: AVCaptureDeviceInput?",
        "replacementInput = try AVCaptureDeviceInput(device: newDevice)",
        "let previousInput = self.input",
        "guard self.session.canAddInput(replacementInput) else",
        "self.session.canAddInput(previousInput)",
        "self.session.addInput(previousInput)\n                    self.input = previousInput",
        'NSLog("Skin capture session rejected the replacement device input.")',
        "guard let replacementInput = replacementInput else",
        "getDeviceSettings(device: replacementInput.device)",
    ):
        if skin_switch_start < 0 or skin_switch_end < 0 or fragment not in skin_switch:
            errors.append(f"Skin.selectedDevice must retain transactional replacement via {fragment!r}")
    replacement_build = skin_switch.find("replacementInput = try AVCaptureDeviceInput(device: newDevice)")
    configuration_start = skin_switch.find("self.session.beginConfiguration()")
    previous_removal = skin_switch.find("self.session.removeInput(previousInput)")
    admission_check = skin_switch.find("guard self.session.canAddInput(replacementInput) else")
    replacement_add = skin_switch.find("self.session.addInput(replacementInput)")
    if min(replacement_build, configuration_start, previous_removal, admission_check, replacement_add) < 0 or not (
        replacement_build < configuration_start < previous_removal < admission_check < replacement_add
    ):
        errors.append("Skin.selectedDevice must prepare, configure, validate, and add replacements in order")
    if skin_switch.count("beginConfiguration()") != 1 or skin_switch.count("commitConfiguration()") != 1:
        errors.append("Skin.selectedDevice must keep one balanced configuration transaction")
    if "defer {\n                self.session.commitConfiguration()\n                self.updateAspect()\n                self.setThisAsSelectedDevice()\n            }" not in skin_switch:
        if "defer {\n                self.session.commitConfiguration()\n                self.replaceFormatObserver()\n                self.updateAspect()\n                self.setThisAsSelectedDevice()\n            }" not in skin_switch:
            errors.append("Skin.selectedDevice must preserve post-transaction observer, aspect, and selection updates")

    for fragment in (
        "guard windowSize.isFinitePositive && screenFrame.hasUsableWindowGeometry else",
        "guard windowRect.hasUsableWindowGeometry else",
        "self.device.skinSize.isFinitePositive",
        "originalPreviewViewBounds.size.isFinitePositive",
    ):
        if fragment not in skin:
            errors.append(f"Skin layout must reject unusable geometry via {fragment!r}")

    mouse_entered_start = skin.find("override func mouseEntered")
    mouse_exited_start = skin.find("override func mouseExited", mouse_entered_start)
    mouse_down_start = skin.find("override func mouseDown", mouse_exited_start)
    mouse_entered = skin[mouse_entered_start:mouse_exited_start]
    mouse_exited = skin[mouse_exited_start:mouse_down_start]
    pointer_guard = "guard let resizeHandle = self.resizeHandle else"
    if (
        min(mouse_entered_start, mouse_exited_start, mouse_down_start) < 0
        or pointer_guard not in mouse_entered
        or pointer_guard not in mouse_exited
        or "self.resizeHandle.isHidden" in mouse_entered + mouse_exited
    ):
        errors.append("Skin pointer hover handlers must guard the resize handle outlet")

    for swift_path in sorted((ROOT / "ScreenShare").glob("*.swift")):
        for line_number, line in enumerate(swift_path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue
            if re.search(r"\bprint(?:ln)?\s*\(", stripped):
                errors.append(f"{swift_path.relative_to(ROOT)}:{line_number} must not use print/println for app logging")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("project", "behavior"), required=True)
    args = parser.parse_args()

    errors = project_checks() if args.mode == "project" else behavior_checks()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"{args.mode} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
