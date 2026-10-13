"""Failures and subsequent successes remain independent historical records."""

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fox_engine.evidence import EvidenceError, EvidenceJournal, verify_journal
from fox_engine.security import AuthorityShield, AuthorizationError, Grant, Operation


def synthetic_record(record_id="failed-run", exit_status=1):
    return {
        "record_id": record_id, "project_id": "synthetic-project",
        "timestamp": "2026-10-13T12:00:00+00:00",
        "observed_condition": "Synthetic validator rejected a disallowed inline program",
        "source": "synthetic-fixture", "tool_id": "fixture-validator",
        "artifact_hashes": {"fixture.txt": hashlib.sha256(b"synthetic").hexdigest()},
        "command_summary": "python synthetic_validator.py fixture.txt", "exit_status": exit_status,
        "hypothesis_links": [{"hypothesis_id": "validator-defect", "relation": "CONTRADICTS"}],
        "decision_ids": ["investigate-validator"], "confidence_qualification": "Synthetic observation only",
        "environment": {"platform": "synthetic"},
        "reproduction_steps": ["Run the synthetic fixture validator"],
    }


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "journal.jsonl"
        self.journal = EvidenceJournal(self.path)
        self.now = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)
        self.shield = AuthorityShield(self.root, clock=lambda: self.now)
        self.grant = Grant("fixture", Operation.WRITE_EVIDENCE, str(self.path), "evidence-journal",
                           "2026-10-13T11:00:00Z", "2026-10-13T13:00:00Z")
        self.permit = self.shield.authorize(Operation.WRITE_EVIDENCE, self.path,
                                           resource="evidence-journal", grant=self.grant)

    def append(self, record):
        return self.journal.append(record, permit=self.permit)

    def test_constructor_and_read_do_not_create_files(self):
        self.assertFalse(self.path.exists())
        with self.assertRaises(FileNotFoundError):
            self.journal.verify()
        self.assertFalse(self.path.exists())

    def test_append_without_exact_live_permit_is_denied(self):
        with self.assertRaises(AuthorizationError):
            self.journal.append(synthetic_record())
        readonly = self.shield.authorize(Operation.READ_EVIDENCE, self.path)
        with self.assertRaises(AuthorizationError):
            self.journal.append(synthetic_record(), permit=readonly)
        self.now = datetime(2026, 10, 13, 13, 0, tzinfo=timezone.utc)
        with self.assertRaises(AuthorizationError):
            self.append(synthetic_record())
        self.assertFalse(self.path.exists())

    def test_failure_success_and_contradiction_are_preserved(self):
        original = synthetic_record()
        digest = self.append(original)
        self.assertEqual(64, len(digest))
        first_bytes = self.path.read_bytes()
        original["observed_condition"] = "caller mutated its copy"
        corrected = synthetic_record("corrected-run", 0)
        corrected["observed_condition"] = "Corrected synthetic evidence passed the unchanged validator"
        self.append(corrected)
        records = verify_journal(self.path)
        self.assertTrue(self.path.read_bytes().startswith(first_bytes))
        self.assertEqual([1, 0], [item["exit_status"] for item in records])
        self.assertNotEqual(original["observed_condition"], records[0]["observed_condition"])
        self.assertEqual("CONTRADICTS", records[0]["hypothesis_links"][0]["relation"])

    def test_duplicate_identity_cannot_rewrite_history(self):
        self.append(synthetic_record())
        before = self.path.read_bytes()
        with self.assertRaises(EvidenceError):
            self.append(synthetic_record(exit_status=0))
        self.assertEqual(before, self.path.read_bytes())

    def test_tamper_rejected_by_reader_and_append_without_repair(self):
        self.append(synthetic_record())
        entry = json.loads(self.path.read_text(encoding="utf-8"))
        entry["record"]["exit_status"] = 0
        tampered = (json.dumps(entry) + "\n").encode()
        self.path.write_bytes(tampered)
        with self.assertRaises(EvidenceError):
            verify_journal(self.path)
        with self.assertRaises(EvidenceError):
            self.append(synthetic_record("next"))
        self.assertEqual(tampered, self.path.read_bytes())

    def test_torn_write_is_preserved_and_blocks_append(self):
        self.append(synthetic_record())
        torn = self.path.read_bytes() + b'{"format_version":1'
        self.path.write_bytes(torn)
        with self.assertRaises(EvidenceError):
            self.journal.verify()
        with self.assertRaises(EvidenceError):
            self.append(synthetic_record("next"))
        self.assertEqual(torn, self.path.read_bytes())

    def test_sequence_reordering_and_duplicate_lines_are_rejected(self):
        self.append(synthetic_record())
        self.append(synthetic_record("second"))
        lines = self.path.read_bytes().splitlines(keepends=True)
        for data in (lines[1] + lines[0], lines[0] + lines[0]):
            with self.subTest(data=data[:20]):
                self.path.write_bytes(data)
                with self.assertRaises(EvidenceError):
                    self.journal.verify()

    def test_duplicate_json_keys_are_rejected(self):
        self.append(synthetic_record())
        data = self.path.read_bytes().replace(b'"format_version":1', b'"format_version":1,"format_version":1')
        self.path.write_bytes(data)
        with self.assertRaises(EvidenceError):
            self.journal.verify()

    def test_duplicate_identity_is_rejected_even_with_recomputed_chain(self):
        self.append(synthetic_record())
        first = json.loads(self.path.read_text(encoding="utf-8"))
        duplicate = dict(first)
        duplicate["sequence"] = 2
        duplicate["previous_hash"] = first["entry_hash"]
        body = {key: value for key, value in duplicate.items() if key != "entry_hash"}
        duplicate["entry_hash"] = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()
        with self.path.open("ab") as stream:
            stream.write((json.dumps(duplicate) + "\n").encode())
        with self.assertRaisesRegex(EvidenceError, "Duplicate evidence record identity"):
            verify_journal(self.path)

    def test_existing_journal_is_unchanged_by_independent_verification(self):
        self.append(synthetic_record())
        before = self.path.read_bytes()
        verify_journal(self.path)
        self.assertEqual(before, self.path.read_bytes())

    def test_invalid_record_creates_no_journal(self):
        record = synthetic_record()
        record["exit_status"] = "success"
        with self.assertRaises(EvidenceError):
            self.append(record)
        self.assertFalse(self.path.exists())

    def test_boolean_envelope_version_is_not_integer_one(self):
        self.append(synthetic_record())
        entry = json.loads(self.path.read_text(encoding="utf-8"))
        entry["format_version"] = True
        self.path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        with self.assertRaises(EvidenceError):
            self.journal.verify()

    def test_trusted_anchor_verifies_exact_nonempty_snapshot(self):
        first = synthetic_record()
        second = synthetic_record("corrected-run", 0)
        self.append(first)
        head_hash = self.append(second)
        before = self.path.read_bytes()
        for verifier in (
            lambda **kwargs: verify_journal(self.path, **kwargs), self.journal.verify,
        ):
            with self.subTest(verifier=verifier):
                self.assertEqual([first, second], verifier(expected_count=2, expected_head_hash=head_hash))
                self.assertEqual([first, second], verifier())
        self.assertEqual(before, self.path.read_bytes())

    def test_empty_journal_anchor_uses_zero_count_and_genesis_hash(self):
        self.path.write_bytes(b"")
        self.assertEqual([], self.journal.verify(expected_count=0, expected_head_hash="0" * 64))
        self.assertEqual([], verify_journal(self.path, expected_count=0, expected_head_hash="0" * 64))
        self.assertEqual(b"", self.path.read_bytes())

    def test_trusted_anchor_detects_suffix_and_complete_truncation(self):
        self.append(synthetic_record())
        first_line = self.path.read_bytes()
        head_hash = self.append(synthetic_record("second", 0))
        for truncated in (first_line, b""):
            with self.subTest(truncated_count=bool(truncated)):
                self.path.write_bytes(truncated)
                # Internally consistent prefixes still pass unanchored checks.
                self.assertEqual(int(bool(truncated)), len(verify_journal(self.path)))
                with self.assertRaisesRegex(EvidenceError, "record count differs"):
                    self.journal.verify(expected_count=2, expected_head_hash=head_hash)
                self.assertEqual(truncated, self.path.read_bytes())

    def test_trusted_anchor_detects_fully_recomputed_replacement(self):
        self.append(synthetic_record())
        head_hash = self.append(synthetic_record("second", 0))
        replacement_path = self.root / "replacement.jsonl"
        replacement_grant = replace(self.grant, path=str(replacement_path))
        replacement_permit = self.shield.authorize(
            Operation.WRITE_EVIDENCE, replacement_path,
            resource="evidence-journal", grant=replacement_grant,
        )
        replacement_journal = EvidenceJournal(replacement_path)
        changed_record = synthetic_record(exit_status=0)
        changed_record["observed_condition"] = "Synthetic rewritten history; no longer the retained failure"
        replacement_journal.append(changed_record, permit=replacement_permit)
        replacement_journal.append(synthetic_record("second", 0), permit=replacement_permit)
        replacement_bytes = replacement_path.read_bytes()
        self.path.write_bytes(replacement_bytes)
        self.assertEqual(changed_record, verify_journal(self.path)[0])
        with self.assertRaisesRegex(EvidenceError, "head hash differs"):
            verify_journal(self.path, expected_count=2, expected_head_hash=head_hash)
        self.assertEqual(replacement_bytes, self.path.read_bytes())

    def test_later_legitimate_append_requires_a_new_snapshot_anchor(self):
        old_head_hash = self.append(synthetic_record())
        new_head_hash = self.append(synthetic_record("second", 0))
        with self.assertRaisesRegex(EvidenceError, "record count differs"):
            self.journal.verify(expected_count=1, expected_head_hash=old_head_hash)
        self.assertEqual(2, len(self.journal.verify(expected_count=2, expected_head_hash=new_head_hash)))

    def test_malformed_anchor_arguments_are_rejected_before_io(self):
        valid_hash = "a" * 64
        cases = [
            {"expected_count": 1}, {"expected_head_hash": valid_hash},
            {"expected_count": True, "expected_head_hash": valid_hash},
            {"expected_count": False, "expected_head_hash": "0" * 64},
            {"expected_count": -1, "expected_head_hash": valid_hash},
            {"expected_count": 1.0, "expected_head_hash": valid_hash},
            {"expected_count": "1", "expected_head_hash": valid_hash},
            {"expected_count": 1, "expected_head_hash": "A" * 64},
            {"expected_count": 1, "expected_head_hash": "g" * 64},
            {"expected_count": 1, "expected_head_hash": "a" * 63},
            {"expected_count": 1, "expected_head_hash": "a" * 65},
            {"expected_count": 1, "expected_head_hash": b"a" * 64},
            {"expected_count": 0, "expected_head_hash": valid_hash},
        ]
        for verifier in (
            lambda **kwargs: verify_journal(self.path, **kwargs), self.journal.verify,
        ):
            for arguments in cases:
                with self.subTest(arguments=arguments), self.assertRaises(EvidenceError):
                    verifier(**arguments)
        self.assertFalse(self.path.exists())

    def test_valid_anchor_does_not_create_a_missing_journal(self):
        with self.assertRaises(FileNotFoundError):
            self.journal.verify(expected_count=0, expected_head_hash="0" * 64)
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
