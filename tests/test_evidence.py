"""Failures and subsequent successes remain independent historical records."""

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


if __name__ == "__main__":
    unittest.main()
