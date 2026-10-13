"""Regression probes from independent review; fixtures are entirely synthetic."""

from copy import deepcopy
import importlib.util
import json
import subprocess
import sys
import unittest

from fox_engine.contracts import ContractError, SCHEMAS, content_hash, validate_record
from fox_engine.core import FoxEngine, verify_decision
from fox_engine.hypotheses import competing_hypotheses, evaluate
from fox_engine.adapters.stdio import MAX_LINE_BYTES


def problem():
    return {
        "problem_id": "synthetic-problem", "project_id": "synthetic-project",
        "description": "Investigate rejection of a synthetic fixture.",
        "domain": "validation", "assumptions": [], "constraints": [],
        "desired_outcome": "Distinguish a correct validator from invalid test data.",
    }


def evidence():
    return {
        "record_id": "synthetic-observation", "project_id": "synthetic-project",
        "timestamp": "2026-10-13T00:00:00Z",
        "observed_condition": "Synthetic validator rejected a nonconforming fixture.",
        "source": "synthetic fixture", "tool_id": "synthetic-validator",
        "artifact_hashes": {}, "command_summary": "synthetic-contract-probe",
        "exit_status": 1, "hypothesis_links": [], "decision_ids": [],
        "confidence_qualification": "Synthetic observation, not an external result.",
        "environment": {"fixture": "synthetic"},
        "reproduction_steps": ["Run the synthetic fixture against its unchanged contract."],
    }


def rehash(decision):
    decision["decision_id"] = "decision:" + content_hash({
        key: value for key, value in decision.items() if key != "decision_id"
    })
    return decision


class AdversarialReviewTests(unittest.TestCase):
    def test_decision_identity_binds_problem_requirements(self):
        engine = FoxEngine()
        original = problem()
        changed = deepcopy(original)
        changed["description"] = "Investigate a different synthetic safety requirement."
        changed["constraints"] = ["Never expose the synthetic service over a network."]
        changed["desired_outcome"] = "Determine whether the synthetic deployment violates isolation."
        self.assertNotEqual(engine.analyze(original)["decision_id"], engine.analyze(changed)["decision_id"])

    def test_reconstruction_rejects_removed_historical_hypothesis(self):
        engine = FoxEngine()
        first = engine.analyze(problem())
        child = engine.analyze(problem(), previous_decision=first)
        child["hypotheses"].pop()
        rehash(child)
        with self.assertRaises(ContractError):
            engine.reconstruct([first, child])

    def test_reconstruction_rejects_rewritten_historical_hypothesis(self):
        engine = FoxEngine()
        first = engine.analyze(problem())
        child = engine.analyze(problem(), previous_decision=first)
        child["hypotheses"][0]["statement"] = "A different claim silently substituted under the old identity."
        rehash(child)
        with self.assertRaises(ContractError):
            engine.reconstruct([child, first])

    def test_valid_maximum_length_hypothesis_id_survives_action_generation(self):
        hypothesis = competing_hypotheses("synthetic-project")[0]
        hypothesis["hypothesis_id"] = "h" * 128
        validate_record("hypothesis", hypothesis)
        decision = FoxEngine().analyze(problem(), hypotheses=[hypothesis])
        verify_decision(decision)

    def test_test_actions_cannot_declare_authorization_unnecessary(self):
        decision = FoxEngine().analyze(problem())
        action = next(
            action for recommendation in decision["recommendations"]
            for action in recommendation["actions"] if action["operation"] == "TEST_EXECUTION"
        )
        action["requires_authorization"] = False
        rehash(decision)
        with self.assertRaises(ContractError):
            verify_decision(decision)

    def test_invalid_timezone_minute_rejected(self):
        record = evidence()
        record["timestamp"] = "2026-10-13T00:00:00+00:60"
        with self.assertRaises(ContractError):
            validate_record("evidence", record)

    def test_standalone_evaluation_cannot_erase_historical_evidence(self):
        hypothesis = competing_hypotheses("synthetic-project")[0]
        record = evidence()
        record["hypothesis_links"] = [{
            "hypothesis_id": hypothesis["hypothesis_id"], "relation": "CONTRADICTS",
        }]
        rejected = evaluate(hypothesis, [record])
        self.assertEqual(rejected["status"], "REJECTED_HYPOTHESIS")
        with self.assertRaises(ContractError):
            evaluate(rejected, [])

    def test_transport_recovers_after_oversized_duplicate_and_deep_requests(self):
        valid = json.dumps({
            "contract_version": "1.0", "request_id": "synthetic-request",
            "operation": "strategies", "payload": {},
        })
        duplicate = valid.replace('"payload": {}', '"payload": {}, "payload": {}')
        nested = json.dumps({
            "contract_version": "1.0", "request_id": "deep-request",
            "operation": "strategies", "payload": {"unexpected": []},
        }).replace('[]', '[' * 70 + '0' + ']' * 70)
        input_data = "x" * (MAX_LINE_BYTES + 1) + "\n" + duplicate + "\n" + nested + "\n" + valid + "\n"
        completed = subprocess.run(
            [sys.executable, "-m", "fox_engine"], input=input_data,
            text=True, capture_output=True, timeout=10, check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stderr, "")
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual([response["ok"] for response in responses], [False, False, False, True])
        self.assertEqual(responses[-1]["request_id"], "synthetic-request")
        self.assertEqual(len(responses[-1]["result"]), 8)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "development jsonschema dependency unavailable")
    def test_integral_json_number_parity(self):
        from jsonschema import Draft202012Validator, FormatChecker

        record = evidence()
        record["exit_status"] = 1.0
        Draft202012Validator(SCHEMAS["evidence"], format_checker=FormatChecker()).validate(record)
        validate_record("evidence", record)


if __name__ == "__main__":
    unittest.main()
