#!/usr/bin/env python3
import argparse
import plistlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_plist(relative_path):
    return plistlib.loads((ROOT / relative_path).read_bytes())


def require_paths():
    errors = []
    for relative_path in (
        "build.sh",
        "Screenshare.xcodeproj/project.pbxproj",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/Screenshare.xcscheme",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUnitTests.xcscheme",
        "Screenshare.xcodeproj/xcshareddata/xcschemes/ScreenshareUITests.xcscheme",
        "ScreenShare/Info.plist",
        "ScreenShare/Screenshare.entitlements",
        "ScreenShare/AppDelegate.swift",
        "ScreenShare/Skin.swift",
    ):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")
    return errors


def project_checks():
    errors = require_paths()
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

    project = read_text("Screenshare.xcodeproj/project.pbxproj")
    for fragment in (
        "ScreenShareTests",
        "ScreenshareUITests",
        'CODE_SIGN_ENTITLEMENTS = "$(PROJECT_DIR)/ScreenShare/Screenshare.entitlements";',
        "MACOSX_DEPLOYMENT_TARGET = 10.9;",
    ):
        if fragment not in project:
            errors.append(f"project is missing expected setting: {fragment}")

    return errors


def behavior_checks():
    errors = require_paths()
    if errors:
        return errors

    app_delegate = read_text("ScreenShare/AppDelegate.swift")
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
