from copy import deepcopy
import unittest
from fox_engine import FoxEngine
from fox_engine.contracts import PRINCIPLES, ContractError, content_hash
from fox_engine.hypotheses import competing_hypotheses


def problem():
    return {"problem_id": "p1", "project_id": "synthetic", "description": "Evidence index rejected a fixture.",
            "domain": "validation", "assumptions": ["The validator may be defective."],
            "constraints": ["Preserve the validation rule."], "desired_outcome": "Explain the rejection."}


def observation(record_id="failed-run", relation="CONTRADICTS", exit_status=1):
    return {"record_id": record_id, "project_id": "synthetic", "timestamp": "2026-01-01T00:00:00Z",
        "observed_condition": "Synthetic fixture violates the unchanged contract.",
        "source": "synthetic unit fixture", "tool_id": "unittest", "artifact_hashes": {},
        "command_summary": "synthetic control", "exit_status": exit_status,
        "hypothesis_links": [{"hypothesis_id": "implementation_defect", "relation": relation}],
        "decision_ids": [], "confidence_qualification": "Synthetic observation, no real system claim.",
        "environment": {"fixture": "synthetic"}, "reproduction_steps": ["Run tests/test_core.py."]}


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.engine = FoxEngine()

    def test_deterministic_no_mutation_and_all_principles(self):
        p, evidence = problem(), [observation("z"), observation("a")]
        original = deepcopy(evidence)
        first = self.engine.analyze(p, evidence)
        second = self.engine.analyze(p, list(reversed(evidence)))
        self.assertEqual(first, second)
        self.assertEqual(evidence, original)
        self.assertEqual(first["principles"], list(PRINCIPLES))
        self.assertEqual(len(first["hypotheses"]), 8)
        self.assertIn("VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION",
                      next(r["rationale"] for r in first["recommendations"] if r["strategy_id"] == "FOX"))

    def test_contradictory_evidence_is_retained_and_revision_reconstructs(self):
        failure = observation()
        first = self.engine.analyze(problem(), [failure])
        later = observation("later-control", "SUPPORTS", 0)
        second = self.engine.analyze(problem(), [failure, later], previous_decision=first)
        subject = next(h for h in second["hypotheses"] if h["hypothesis_id"] == "implementation_defect")
        self.assertEqual(subject["status"], "UNRESOLVED")
        self.assertEqual(subject["evidence_ids"], ["failed-run", "later-control"])
        self.assertEqual(second["revisions"][0]["previous_status"], "REJECTED_HYPOTHESIS")
        self.assertEqual(self.engine.reconstruct([second, first]), [first, second])

    def test_nonreproduction_is_not_resolution(self):
        successful = observation("pass", "CONTEXT", 0)
        decision = self.engine.analyze(problem(), [successful])
        self.assertFalse(any(h["status"] == "VERIFIED_CONCLUSION" for h in decision["hypotheses"]))

    def test_support_is_not_empirical_probability_or_verification(self):
        decision = self.engine.analyze(problem(), [observation(relation="SUPPORTS")])
        subject = next(h for h in decision["hypotheses"] if h["hypothesis_id"] == "implementation_defect")
        self.assertEqual(subject["status"], "HYPOTHESIS")
        self.assertNotIn("probability", subject)
        for recommendation in decision["recommendations"]:
            for action in recommendation["actions"]:
                if action["operation"] == "TEST_EXECUTION":
                    self.assertTrue(action["requires_authorization"])

    def test_revision_rejects_evidence_removal_or_edit(self):
        evidence = [observation()]
        first = self.engine.analyze(problem(), evidence)
        for revised in [[], [{**evidence[0], "exit_status": 0}]]:
            with self.subTest(revised=revised), self.assertRaises(ContractError):
                self.engine.analyze(problem(), revised, previous_decision=first)

    def test_revision_rejects_rewritten_hypotheses(self):
        first = self.engine.analyze(problem())
        edited = deepcopy(first["hypotheses"])
        edited[0]["statement"] = "Replacement of historical meaning"
        for revised in (edited, first["hypotheses"][1:]):
            with self.assertRaises(ContractError):
                self.engine.analyze(problem(), hypotheses=revised, previous_decision=first)

    def test_bad_references_and_cross_project_inputs_rejected(self):
        bad = observation()
        bad["hypothesis_links"][0]["hypothesis_id"] = "missing"
        for evidence in [[bad], [observation(), observation()], [{**observation(), "project_id": "other"}]]:
            with self.assertRaises(ContractError):
                self.engine.analyze(problem(), evidence)

    def test_reconstruction_rejects_tampering_holes_and_forks(self):
        first = self.engine.analyze(problem())
        second = self.engine.analyze(problem(), [observation()], previous_decision=first)
        third = self.engine.analyze(problem(), [observation("alternative")], previous_decision=first)
        damaged = deepcopy(first)
        damaged["unresolved"] = []
        for lineage in [[damaged], [second], [first, second, third], [first, first]]:
            with self.assertRaises(ContractError):
                self.engine.reconstruct(lineage)

    def test_repeated_evidence_does_not_reopen_status(self):
        first = self.engine.analyze(problem(), [observation()])
        second = self.engine.analyze(problem(), [observation()], previous_decision=first)
        self.assertEqual(second["revisions"], [])
        self.assertEqual(first["hypotheses"], second["hypotheses"])


if __name__ == "__main__":
    unittest.main()
