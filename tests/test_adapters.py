import json
import subprocess
import sys
import unittest
from fox_engine.adapters.stdio import handle_request, MAX_LINE_BYTES
from fox_engine.contracts import validate_record
from test_core import problem, observation


def request(operation="analyze", payload=None):
    return {"contract_version": "1.0", "request_id": "synthetic-request", "operation": operation,
            "payload": payload if payload is not None else {"problem": problem()}}


class AdapterTests(unittest.TestCase):
    def test_sdk_adapter_agreement_and_operations(self):
        for operation, payload in [("analyze", {"problem": problem()}), ("strategies", {}),
            ("discover_architecture", {"vision": "A synthetic sensor interface"}),
            ("verify_evidence", {"records": [observation()]})]:
            with self.subTest(operation=operation):
                result = handle_request(request(operation, payload))
                self.assertTrue(result["ok"])
                validate_record("response", result)

    def test_unknown_operations_versions_payloads_and_no_paths(self):
        fixtures = [request("execute"), {**request(), "contract_version": "2.0"},
                    request("verify_evidence", {"path": "private-file"}), request("strategies", {"command": "ignored"}),
                    request("analyze", {"problem": problem(), "evidence": None}), None, []]
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                result = handle_request(fixture)
                self.assertFalse(result["ok"])
                self.assertIsNone(result["result"])

    def test_stdio_is_line_framed_and_recovers_after_invalid_request(self):
        text = '{"request_id":"sensitive-value","request_id":"duplicate"}\n' + json.dumps(request()) + "\n"
        proc = subprocess.run([sys.executable, "-m", "fox_engine"], input=text, text=True, capture_output=True, timeout=15)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        responses = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual([r["ok"] for r in responses], [False, True])
        self.assertNotIn("sensitive-value", proc.stdout)

    def test_oversized_and_invalid_utf8_requests_fail_closed(self):
        data = b"x" * (MAX_LINE_BYTES + 8) + b"\n\xff\n" + json.dumps(request("strategies", {})).encode() + b"\n"
        proc = subprocess.run([sys.executable, "-m", "fox_engine"], input=data, capture_output=True, timeout=15)
        responses = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual([r["ok"] for r in responses], [False, False, True])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, b"")


if __name__ == "__main__":
    unittest.main()
