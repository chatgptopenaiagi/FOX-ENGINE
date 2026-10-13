"""Synthetic validator investigation; fixture command strings are never run."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json
from pathlib import Path

from fox_engine import FoxEngine
from fox_engine.contracts import content_hash
from fox_engine.hypotheses import competing_hypotheses


PROJECT = "synthetic-evidence-index"
TACTIC = "VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION"


def validate_fixture(fixture: dict) -> dict:
    """Small stand-in policy, independent of any real CAE implementation.

    Command strings are inert example data. Presence of inline_program is
    forbidden; a nonempty command token list is required. Nothing is executed.
    """
    if "inline_program" in fixture:
        return {"accepted": False, "exit_status": 1, "reason": "INLINE_PROGRAM_DISALLOWED"}
    command = fixture.get("command")
    if not isinstance(command, list) or not command or any(not isinstance(token, str) or not token for token in command):
        return {"accepted": False, "exit_status": 1, "reason": "INVALID_COMMAND_DESCRIPTION"}
    return {"accepted": True, "exit_status": 0, "reason": "ACCEPTED"}


def _record(fixture: dict, result: dict, links: list[dict]) -> dict:
    return {
        "record_id": fixture["run_id"], "project_id": PROJECT,
        "timestamp": "2026-01-01T00:00:00Z",
        "observed_condition": "Synthetic stand-in result: " + result["reason"],
        "source": "examples/evidence_index_failure/fixtures.json",
        "tool_id": "synthetic-stand-in-validator-v1",
        "artifact_hashes": {fixture["run_id"]: content_hash(fixture)},
        "command_summary": "Call validate_fixture on inert JSON; no command tokens are executed",
        "exit_status": result["exit_status"], "hypothesis_links": links,
        "decision_ids": [], "confidence_qualification": "Synthetic fixture observation; not evidence about CAE or production correctness",
        "environment": {"runtime": "deterministic-in-process-synthetic", "policy": "inline_program field forbidden"},
        "reproduction_steps": ["Run PYTHONPATH=src python examples/evidence_index_failure/run.py from the repository root"],
    }


def run() -> dict:
    fixtures = json.loads(Path(__file__).with_name("fixtures.json").read_text(encoding="utf-8"))
    fingerprint_before = content_hash(inspect.getsource(validate_fixture))
    problem = {
        "problem_id": "evidence-index-rejection", "project_id": PROJECT,
        "description": "Six synthetic diagnostic entries were rejected by a stand-in evidence validator.",
        "domain": "validation", "assumptions": ["A rejection might indicate a validator defect."],
        "constraints": ["Preserve rejected fixtures and the original rule.", "Never execute fixture command strings."],
        "desired_outcome": "Compare rejected entries with corrected entries and a valid control before proposing a validator change.",
    }
    hypotheses = competing_hypotheses(PROJECT)
    for hypothesis in hypotheses:
        if hypothesis["hypothesis_id"] == "implementation_defect":
            hypothesis["statement"] = "The stand-in validator misclassifies at least one of these thirteen synthetic fixtures under its declared rule."
        elif hypothesis["hypothesis_id"] == "correct_validator":
            hypothesis["statement"] = "The stand-in validator correctly classifies the thirteen supplied synthetic fixtures."
    originals = fixtures["rejected"]
    observations = [
        _record(fixture, validate_fixture(fixture), [
            {"hypothesis_id": "implementation_defect", "relation": "CONTEXT"},
            {"hypothesis_id": "correct_validator", "relation": "CONTEXT"},
        ]) for fixture in originals
    ]
    engine = FoxEngine()
    initial = engine.analyze(problem, observations, hypotheses=hypotheses)
    preserved = deepcopy(observations)
    controls = fixtures["corrected"] + [fixtures["control"]]
    matrix_matches_expectations = (
        all(validate_fixture(fixture)["exit_status"] == 1 for fixture in originals)
        and all(validate_fixture(fixture)["exit_status"] == 0 for fixture in controls)
    )
    # These links summarize a fixture-specific comparison with the explicit
    # expected classifications. They are caller assertions, not inferred proof.
    observations += [
        _record(fixture, validate_fixture(fixture), [
            {"hypothesis_id": "implementation_defect", "relation": "CONTRADICTS" if matrix_matches_expectations else "SUPPORTS"},
            {"hypothesis_id": "correct_validator", "relation": "SUPPORTS" if matrix_matches_expectations else "CONTRADICTS"},
            {"hypothesis_id": "invalid_input", "relation": "SUPPORTS" if matrix_matches_expectations else "CONTEXT"},
        ]) for fixture in controls
    ]
    for record in observations[len(preserved):]:
        record["observed_condition"] += f"; full fixture matrix matches six rejections and seven acceptances: {matrix_matches_expectations}"
    revised = engine.analyze(problem, observations, previous_decision=initial)
    return {
        "scenario": "synthetic-evidence-index-investigation", "synthetic": True, "tactic": TACTIC,
        "validator_unchanged": fingerprint_before == content_hash(inspect.getsource(validate_fixture)),
        "validator_source_hash": fingerprint_before,
        "historical_records_unchanged": observations[:len(preserved)] == preserved,
        "matrix_matches_expectations": matrix_matches_expectations,
        "replayed_rejections": [validate_fixture(fixture)["exit_status"] for fixture in originals],
        "failed_records": sum(record["exit_status"] != 0 for record in observations),
        "passing_records": sum(record["exit_status"] == 0 for record in observations),
        "evidence": observations, "initial_decision": initial, "revised_decision": revised,
        "verification_scope": "Thirteen synthetic fixture classifications only; real CAE behavior was not inspected or verified.",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("evidence", "initial_decision", "revised_decision")}, sort_keys=True))
