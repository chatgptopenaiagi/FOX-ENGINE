"""Adversarial scope checks using synthetic resources inside this repository."""

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from fox_engine.security import AuthorityShield, AuthorizationError, Grant, Operation


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "workspace"
        self.root.mkdir()
        self.now = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        self.shield = AuthorityShield(self.root, clock=lambda: self.now)
        self.path = self.root / "evidence.jsonl"
        self.grant = Grant(
            "synthetic-grant", Operation.WRITE_EVIDENCE, str(self.path), "evidence-journal",
            "2026-10-13T11:00:00+00:00", "2026-10-13T13:00:00+00:00",
        )

    def authorize(self, **kwargs):
        parameters = dict(operation=Operation.WRITE_EVIDENCE, path=self.path,
                          resource="evidence-journal", grant=self.grant)
        parameters.update(kwargs)
        return self.shield.authorize(**parameters)

    def test_default_is_read_only(self):
        self.shield.authorize(Operation.ANALYZE, self.path)
        self.shield.authorize(Operation.READ_EVIDENCE, self.path)
        for operation in (Operation.WRITE_EVIDENCE, Operation.CREATE_FILE,
                          Operation.MODIFY_FILE, Operation.EXECUTE_TEST,
                          Operation.CREATE_PROCESS, Operation.INSTALL_DEPENDENCY):
            with self.subTest(operation=operation), self.assertRaises(AuthorizationError):
                self.shield.authorize(operation, self.path)
        self.assertFalse(self.path.exists(), "Policy checks must not create a resource")

    def test_grant_is_exact_in_all_dimensions(self):
        permit = self.authorize()
        permit.require(Operation.WRITE_EVIDENCE, self.path, "evidence-journal")
        for kwargs in (
            {"operation": Operation.CREATE_FILE}, {"path": self.root / "other.jsonl"},
            {"resource": "other-resource"}, {"path": self.base / "outside.jsonl"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(AuthorizationError):
                self.authorize(**kwargs)
        with self.assertRaises(AuthorizationError):
            permit.require(Operation.WRITE_EVIDENCE, self.root / "other", "evidence-journal")
        with self.assertRaises(AuthorizationError):
            permit.require(Operation.CREATE_FILE, self.path, "evidence-journal")

    def test_lifetime_and_reuse_are_checked(self):
        permit = self.authorize()
        self.now = datetime(2026, 10, 13, 13, 0, tzinfo=timezone.utc)
        with self.assertRaises(AuthorizationError):
            self.authorize()
        with self.assertRaises(AuthorizationError):
            permit.require(Operation.WRITE_EVIDENCE, self.path, "evidence-journal")
        self.now = datetime(2026, 10, 13, 10, 59, tzinfo=timezone.utc)
        with self.assertRaises(AuthorizationError):
            self.authorize()

    def test_ambiguous_lifetimes_fail_closed(self):
        for kwargs in (
            {"not_before": "2026-10-13T11:00:00"}, {"expires_at": "not-a-date"},
            {"expires_at": "2026-10-13T10:00:00Z"}, {"resource": ""},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(AuthorizationError):
                replace(self.grant, **kwargs)
        self.now = datetime(2026, 10, 13, 12, 0)
        with self.assertRaises(AuthorizationError):
            self.authorize()

    def test_traversal_device_stream_and_sensitive_paths_are_rejected(self):
        paths = [
            "../outside", "folder/../../outside", "folder/../same", "C:relative",
            "evidence.jsonl:secret", "NUL", "con.txt", "folder/LPT1.log", "file.",
            "file ", "//server/share", "\\\\?\\C:\\device", ".env", ".env.local",
            ".git/config", ".ssh/id_rsa", "credentials.json", "folder\x00bad",
        ]
        for path in paths:
            with self.subTest(path=path), self.assertRaises(AuthorizationError):
                self.shield.authorize(Operation.ANALYZE, path)

    def test_forbidden_operations_cannot_be_unlocked_by_a_grant(self):
        operations = [Operation.READ_CREDENTIALS, Operation.DELETE, Operation.MODIFY_SECURITY,
                      Operation.ADMINISTER_ACCOUNT, Operation.PRIVILEGED_COMMAND,
                      Operation.EXPOSE_NETWORK, Operation.PUBLISH,
                      Operation.MODIFY_PROTECTED_INSTALLATION]
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(AuthorizationError):
                self.authorize(operation=operation, grant=replace(self.grant, operation=operation))
        with self.assertRaises(AuthorizationError):
            self.authorize(operation="UNKNOWN")

    def test_directory_symlinks_cannot_escape_or_alias_scope(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.root / "link"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Creating a test symlink is unavailable: {type(exc).__name__}")
        with self.assertRaises(AuthorizationError):
            self.shield.authorize(Operation.ANALYZE, link / "data")
        link.unlink()
        internal = self.root / "internal"
        internal.mkdir()
        link.symlink_to(internal, target_is_directory=True)
        with self.assertRaises(AuthorizationError):
            self.shield.authorize(Operation.ANALYZE, link / "data")

    def test_permit_rechecks_new_symlink(self):
        permit = self.authorize()
        target = self.root / "alternate.jsonl"
        target.write_text("synthetic", encoding="utf-8")
        try:
            self.path.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Creating a test symlink is unavailable: {type(exc).__name__}")
        with self.assertRaises(AuthorizationError):
            permit.require(Operation.WRITE_EVIDENCE, self.path, "evidence-journal")


if __name__ == "__main__":
    unittest.main()
