"""A controlled, simulated environment comparison, not a machine diagnostic."""

from __future__ import annotations

import json

from fox_engine import FoxEngine
from fox_engine.contracts import content_hash
from fox_engine.hypotheses import competing_hypotheses


PROJECT = "synthetic-environment-comparison"
FIXTURE = {"operation": "transform", "value": 42}
SOURCE_IDENTITY = "synthetic-transform-source-v1"
DEPENDENCY_IDENTITY = "synthetic-dependency-v1"


def synthetic_probe(supports_feature: bool) -> dict:
    """Simulate a precondition mismatch without reading the real environment."""
    if not supports_feature:
        return {"exit_status": 78, "result": "required capability absent"}
    return {"exit_status": 0, "result": "synthetic transform accepted"}


def _record(identity: str, supports_feature: bool, links: list[dict]) -> dict:
    result = synthetic_probe(supports_feature)
    return {
        "record_id": identity, "project_id": PROJECT, "timestamp": "2026-01-01T00:00:00Z",
        "observed_condition": result["result"], "source": "synthetic-runtime-matrix",
        "tool_id": "synthetic-capability-probe-v1",
        "artifact_hashes": {"fixture": content_hash(FIXTURE), "source": content_hash(SOURCE_IDENTITY),
                            "dependency": content_hash(DEPENDENCY_IDENTITY)},
        "command_summary": "Call synthetic_probe with one explicit boolean capability; no real runtime is inspected",
        "exit_status": result["exit_status"], "hypothesis_links": links, "decision_ids": [],
        "confidence_qualification": "Synthetic controlled comparison only; real-world causality remains unverified",
        "environment": {"supports_feature": str(supports_feature).lower(), "dependency": DEPENDENCY_IDENTITY},
        "reproduction_steps": ["Run PYTHONPATH=src python examples/environment_vs_software/run.py from the repository root"],
    }


def run() -> dict:
    problem = {
        "problem_id": "runtime-capability-failure", "project_id": PROJECT,
        "description": "A synthetic transform fails when a required runtime capability is absent.",
        "domain": "environment", "assumptions": ["A failing run might indicate defective source."],
        "constraints": ["Hold source, fixture and dependency identities fixed.", "Preserve the failed observation."],
        "desired_outcome": "Discriminate a capability mismatch from a source failure in a bounded simulated matrix.",
    }
    hypotheses = competing_hypotheses(PROJECT)
    for hypothesis in hypotheses:
        if hypothesis["hypothesis_id"] == "implementation_defect":
            hypothesis["statement"] = "The fixed synthetic transform fails in both capability settings in this two-case matrix."
        if hypothesis["hypothesis_id"] == "incompatible_environment":
            hypothesis["statement"] = "Absence of the declared capability accounts for this simulated failure."
    failed = _record("missing-capability", False, [
        {"hypothesis_id": "implementation_defect", "relation": "CONTEXT"},
        {"hypothesis_id": "incompatible_environment", "relation": "CONTEXT"},
    ])
    engine = FoxEngine()
    initial = engine.analyze(problem, [failed], hypotheses=hypotheses)
    control = _record("supported-control", True, [
        {"hypothesis_id": "implementation_defect", "relation": "CONTRADICTS"},
        {"hypothesis_id": "incompatible_environment", "relation": "SUPPORTS"},
    ])
    evidence = [failed, control]
    revised = engine.analyze(problem, evidence, previous_decision=initial)
    return {
        "scenario": "synthetic-environment-versus-source", "synthetic": True,
        "exit_statuses": [record["exit_status"] for record in evidence],
        "fixed_artifact_identities": failed["artifact_hashes"] == control["artifact_hashes"],
        "evidence": evidence, "initial_decision": initial, "revised_decision": revised,
        "verification_scope": "Two simulated capability settings only; no real platform or dependency compatibility was verified.",
        "unresolved": "A passing simulated control does not establish resolution in a real environment.",
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("evidence", "initial_decision", "revised_decision")}, sort_keys=True))
