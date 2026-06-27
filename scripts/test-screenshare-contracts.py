#!/usr/bin/env python3
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContractMutationTests(unittest.TestCase):
    def copy_repository(self):
        temporary_directory = tempfile.TemporaryDirectory()
        repository = Path(temporary_directory.name) / "ScreenShare"
        shutil.copytree(ROOT, repository, ignore=shutil.ignore_patterns(".git", "DerivedData"))
        self.addCleanup(temporary_directory.cleanup)
        return repository

    def mutate(self, repository, relative_path, original, replacement):
        path = repository / relative_path
        source = path.read_text(encoding="utf-8")
        self.assertIn(original, source, f"missing mutation target in {relative_path}")
        path.write_text(source.replace(original, replacement, 1), encoding="utf-8")

    def assert_behavior_rejects(self, repository, expected_error):
        result = subprocess.run(
            [
                str(repository / "scripts/run-python.sh"),
                "scripts/check-screenshare-source.py",
                "--mode",
                "behavior",
            ],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn(expected_error, result.stderr)

    def test_rejects_late_capture_session_initialization(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Skin.swift",
            "let session = AVCaptureSession()",
            "var session : AVCaptureSession!",
        )
        self.assert_behavior_rejects(
            repository,
            "Skin.session must be initialized before nib-backed preview setup",
        )

    def test_rejects_duplicate_preview_layer_construction(self):
        repository = self.copy_repository()
        path = repository / "ScreenShare/Skin.swift"
        source = path.read_text(encoding="utf-8")
        constructor = "let videoPreviewLayer = AVCaptureVideoPreviewLayer(session: self.session)"
        self.assertEqual(1, source.count(constructor))
        path.write_text(source.replace(constructor, f"{constructor}\n            {constructor}", 1), encoding="utf-8")
        self.assert_behavior_rejects(
            repository,
            "Skin must construct exactly one capture preview layer",
        )

    def test_rejects_unvalidated_saved_window_geometry(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Device.swift",
            "return savedSettingForOrientation(forOrientation: forOrientation).hasUsableWindowGeometry",
            "return true",
        )
        self.assert_behavior_rejects(
            repository,
            "Device saved window geometry must reject non-finite or non-positive sizes",
        )

    def test_rejects_pointer_hover_outlet_force_dereferences(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Skin.swift",
            "guard let resizeHandle = self.resizeHandle else {\n            NSLog(\"Skin pointer resize handle is unavailable.\")\n            return\n        }\n        resizeHandle.isHidden = false",
            "self.resizeHandle.isHidden = false",
        )
        self.assert_behavior_rejects(
            repository,
            "Skin pointer hover handlers must guard the resize handle outlet",
        )

    def test_rejects_accumulating_format_observers(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Skin.swift",
            "formatNotifications.deregisterAll()",
            "",
        )
        self.assert_behavior_rejects(
            repository,
            "Skin device changes must replace the format observer instead of accumulating callbacks",
        )

    def test_rejects_unfiltered_capture_port_selection(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Extensions.swift",
            "ports.first { $0.mediaType == .video }",
            "ports.first",
        )
        self.assert_behavior_rejects(
            repository,
            "capture inputs must select their video stream via 'ports.first { $0.mediaType == .video }'",
        )

    def test_rejects_document_format_observer_replacement_removal(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Document.swift",
            "                self.replaceFormatObserver()\n",
            "",
        )
        self.assert_behavior_rejects(
            repository,
            "Document device transactions must replace the active-port format observer",
        )

    def test_rejects_document_format_notification_registration_removal(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShare/Document.swift",
            "            AVCaptureInput.Port.formatDescriptionDidChangeNotification,\n",
            "",
        )
        self.assert_behavior_rejects(
            repository,
            "Document format observer must preserve 'AVCaptureInput.Port.formatDescriptionDidChangeNotification'",
        )

    def test_rejects_document_aspect_guidance_removal(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "README.md",
            "- Document aspect updates run once after session start and then only for the\n  active input port's format-change notifications; device switches replace the\n  observer and window teardown removes it.\n",
            "",
        )
        result = subprocess.run(
            [
                str(repository / "scripts/run-python.sh"),
                "scripts/check-screenshare-source.py",
                "--mode",
                "project",
            ],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("README.md must document event-driven Document aspect updates", result.stderr)

    def test_rejects_colliding_unit_test_module_name(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "Screenshare.xcodeproj/project.pbxproj",
            "PRODUCT_MODULE_NAME = ScreenshareUnitTests;",
            "PRODUCT_MODULE_NAME = Screenshare;",
        )
        result = subprocess.run(
            [
                str(repository / "scripts/run-python.sh"),
                "scripts/check-screenshare-source.py",
                "--mode",
                "project",
            ],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("Unit test module name must not collide with the app module", result.stderr)

    def test_rejects_obsolete_xctest_measure_api(self):
        repository = self.copy_repository()
        self.mutate(
            repository,
            "ScreenShareTests/ScreenShareTests.swift",
            "self.measure {",
            "self.measureBlock() {",
        )
        result = subprocess.run(
            [
                str(repository / "scripts/run-python.sh"),
                "scripts/check-screenshare-source.py",
                "--mode",
                "project",
            ],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("Unit tests must use the current XCTest measure API", result.stderr)


if __name__ == "__main__":
    unittest.main()
