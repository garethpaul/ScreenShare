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
        run: xcodebuild -version

      - name: Build unsigned macOS app
        run: make build
"""


def read_text(relative_path):
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
    for fragment in ("xcodebuild -project Screenshare.xcodeproj", '-scheme "Screenshare"', "test"):
        if fragment not in build_script:
            errors.append(f"build.sh is missing expected xcodebuild fragment: {fragment}")

    workflow = read_text(".github/workflows/check.yml")
    if workflow != EXPECTED_WORKFLOW:
        errors.append("GitHub Actions workflow must match the reviewed credential-free contract and macOS build baseline")

    makefile = read_text("Makefile")
    for fragment in (
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
        '"$(ROOT)/build.sh"',
        '"$(ROOT)/scripts/check-screenshare-source.py"',
        '"$(ROOT)/Screenshare.xcodeproj"',
        "CODE_SIGNING_ALLOWED=NO",
    ):
        if fragment not in makefile:
            errors.append(f"Makefile is missing root-independent fragment: {fragment}")

    for doc_path in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
        document = re.sub(r"\s+", " ", read_text(doc_path))
        if "GitHub Actions" not in document:
            errors.append(f"{doc_path} must document the GitHub Actions baseline")
        if "capture device switch rollback" not in document.lower():
            errors.append(f"{doc_path} must document capture device switch rollback")
        if "device archive optional binding" not in document.lower():
            errors.append(f"{doc_path} must document device archive optional binding")

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
    skin = read_text("ScreenShare/Skin.swift")
    if "AVCaptureDevice" not in app_delegate + skin:
        errors.append("app must keep AVFoundation device capture code visible")

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
    if "guard let port = self.input?.ports.first" not in document:
        errors.append("Document.updateAspect must optional-bind the capture input port")
    if "let window = self.windowForSheet" not in document:
        errors.append("Document.updateAspect must optional-bind the document window")
    if "private func resetResolutionStatus()" not in document:
        errors.append("Document.updateAspect must centralize resolution fallback state")
    if "private var aspectTimer: Timer?" not in document:
        errors.append("Document must retain its repeating aspect timer for teardown")
    if "aspectTimer?.invalidate()\n        aspectTimer = Timer.scheduledTimer" not in document:
        errors.append("Document preview setup must replace any existing aspect timer")
    if "aspectTimer?.invalidate()\n        aspectTimer = nil\n        self.session.stopRunning()" not in document:
        errors.append("Document window teardown must invalidate and release the aspect timer")
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
    if "defer {\n                self.session.commitConfiguration()\n                self.updateAspect()\n            }" not in document:
        errors.append("Document.selectedDevice must commit its single configuration transaction and refresh aspect state")
    if "guard self.session.canAddInput(replacementInput) else" not in document:
        errors.append("Document.selectedDevice must validate replacement input admission")
    if "self.session.canAddInput(previousInput)" not in document or "self.session.addInput(previousInput)\n                    self.input = previousInput" not in document:
        errors.append("Document.selectedDevice must restore the previous input when replacement admission fails")
    if 'NSLog("Capture session rejected the replacement device input.")' not in document:
        errors.append("Document.selectedDevice must log replacement rejection without device metadata")

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
