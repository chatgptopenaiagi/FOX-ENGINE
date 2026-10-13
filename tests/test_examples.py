"""Exercise reproducible synthetic scenarios and their preserved uncertainty."""

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch

from fox_engine import FoxEngine
from fox_engine.architecture import COMPARISON_DIMENSIONS
from fox_engine.contracts import validate_record
from fox_engine.core import verify_decision


ROOT = Path(__file__).resolve().parents[1]


def load_example(name):
    return runpy.run_path(str(ROOT / "examples" / name / "run.py"))


class ExampleTests(unittest.TestCase):
    def test_six_rejections_survive_correction_with_guard_unchanged(self):
        example = load_example("evidence_index_failure")
        result = example["run"]()
        self.assertEqual(result, example["run"](), "Example records must be reproducible")
        self.assertEqual(6, result["failed_records"])
        self.assertEqual(7, result["passing_records"])
        self.assertTrue(result["validator_unchanged"])
        self.assertTrue(result["historical_records_unchanged"])
        self.assertEqual([1] * 6, result["replayed_rejections"])
        revised = result["revised_decision"]
        verify_decision(result["initial_decision"])
        verify_decision(revised)
        self.assertEqual(13, len(revised["evidence_ids"]))
        self.assertEqual(result["initial_decision"]["decision_id"], revised["previous_decision_id"])
        statuses = {h["hypothesis_id"]: h["status"] for h in revised["hypotheses"]}
        self.assertEqual("REJECTED_HYPOTHESIS", statuses["implementation_defect"])
        self.assertEqual("HYPOTHESIS", statuses["correct_validator"])
        self.assertNotIn("VERIFIED_CONCLUSION", statuses.values())
        self.assertTrue(any(result["tactic"] in recommendation["rationale"]
                            for recommendation in revised["recommendations"]))

    def test_standin_rejects_inline_field_even_when_empty(self):
        validator = load_example("evidence_index_failure")["validate_fixture"]
        self.assertEqual(1, validator({"command": ["inert"], "inline_program": ""})["exit_status"])
        self.assertEqual(1, validator({"command": []})["exit_status"])
        self.assertEqual(0, validator({"command": ["inert"]})["exit_status"])

    def test_broken_guard_reverses_the_example_attribution(self):
        example = load_example("evidence_index_failure")

        def broken_validator(fixture):
            return {"accepted": True, "exit_status": 0, "reason": "ACCEPTED_WITHOUT_CHECKING"}

        with patch.dict(example["run"].__globals__, validate_fixture=broken_validator):
            result = example["run"]()
        self.assertFalse(result["matrix_matches_expectations"])
        statuses = {h["hypothesis_id"]: h["status"] for h in result["revised_decision"]["hypotheses"]}
        self.assertEqual("HYPOTHESIS", statuses["implementation_defect"])
        self.assertEqual("REJECTED_HYPOTHESIS", statuses["correct_validator"])

    def test_environment_comparison_holds_other_identities_fixed(self):
        result = load_example("environment_vs_software")["run"]()
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["fixed_artifact_identities"])
        self.assertEqual([78, 0], result["exit_statuses"])
        for record in result["evidence"]:
            validate_record("evidence", record)
        revised = result["revised_decision"]
        verify_decision(revised)
        self.assertIn("missing-capability", revised["evidence_ids"])
        statuses = {h["hypothesis_id"]: h["status"] for h in revised["hypotheses"]}
        self.assertEqual("HYPOTHESIS", statuses["incompatible_environment"])
        self.assertEqual("REJECTED_HYPOTHESIS", statuses["implementation_defect"])
        self.assertNotIn("VERIFIED_CONCLUSION", statuses.values())

    def test_architectures_remain_competing_complete_proposals(self):
        result = load_example("architecture_discovery")["run"]()
        discovery = result["discovery"]
        self.assertEqual("NONE", discovery["execution_authority"])
        self.assertGreaterEqual(len(discovery["candidates"]), 2)
        self.assertEqual(set(COMPARISON_DIMENSIONS), set(discovery["comparison_dimensions"]))
        for candidate in discovery["candidates"]:
            self.assertTrue(candidate["revisable"])
            self.assertEqual("PROPOSAL", candidate["epistemic_status"])
            self.assertEqual(set(COMPARISON_DIMENSIONS), set(candidate["comparison"]))
        strategies = {r["strategy_id"] for r in result["decision"]["recommendations"]}
        self.assertTrue({"OCTOPUS", "EAGLE"}.issubset(strategies))
        verify_decision(result["decision"])

    def test_integration_request_is_valid_and_sdk_usable(self):
        request_text = (ROOT / "examples/agent_integration/request.json").read_text(encoding="utf-8")
        self.assertEqual(1, len(request_text.splitlines()), "CLI transport requires one complete request per line")
        request = json.loads(request_text)
        validate_record("request", request)
        decision = FoxEngine().analyze(**request["payload"])
        verify_decision(decision)
        self.assertEqual([], decision["evidence_ids"])
        self.assertTrue(decision["unresolved"])
        test_actions = [action for strategy in decision["recommendations"] for action in strategy["actions"]
                        if action["operation"] == "TEST_EXECUTION"]
        self.assertTrue(test_actions)
        self.assertTrue(all(action["requires_authorization"] for action in test_actions))

    def test_integration_fixture_works_through_actual_jsonl_cli(self):
        request_text = (ROOT / "examples/agent_integration/request.json").read_text(encoding="utf-8")
        process = subprocess.run(
            [sys.executable, "-m", "fox_engine"], input=request_text, text=True,
            capture_output=True, cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, check=False,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual(1, len(process.stdout.splitlines()))
        response = json.loads(process.stdout)
        self.assertTrue(response["ok"])
        self.assertEqual("synthetic-agent-request", response["request_id"])
        verify_decision(response["result"])


if __name__ == "__main__":
    unittest.main()
