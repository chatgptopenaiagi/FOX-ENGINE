"""Competing explanations and bounded discriminating tests, never probabilities."""
from copy import deepcopy
from fox_engine.contracts import CATEGORIES, ContractError, validate_record

_EXPLANATIONS = {
    "IMPLEMENTATION_DEFECT": ("The implementation violates the stated contract.",
        "Replay a minimal valid fixture under a known compatible environment; a conforming result contradicts this scoped defect claim."),
    "INVALID_INPUT": ("The rejected input violates the documented input contract.",
        "Validate the exact rejected fixture independently against the unchanged contract; acceptance contradicts invalid-input attribution."),
    "CORRECT_VALIDATOR": ("The validator correctly rejects this nonconforming fixture.",
        "Pair the exact rejected fixture with a minimal valid control; rejection of the valid control contradicts validator correctness for this scope."),
    "INCORRECT_TEST": ("The test setup or assertion differs from the requirement.",
        "Compare the test assertion with an independent requirement-derived oracle; agreement contradicts this test-error explanation."),
    "INCOMPATIBLE_ENVIRONMENT": ("The runtime environment causes the observed failure.",
        "Hold source, fixture and dependency versions fixed; compare isolated supported and suspect environments. Failure in both weakens environment-only attribution."),
    "DEPENDENCY_BEHAVIOR": ("A dependency differs from its assumed behavior.",
        "Run a minimal dependency contract probe across the pinned versions with all other inputs held fixed."),
    "INCOMPLETE_EVIDENCE": ("Missing observations prevent an adequate explanation.",
        "Capture the original exit status, fixture, command summary, environment and reproduction steps; independently replay before claiming resolution."),
    "INCONSISTENT_REQUIREMENT": ("The requirements demand mutually incompatible outcomes.",
        "Construct one concrete fixture subject to both requirements and compare their required outcomes; consistent outcomes contradict this scoped inconsistency."),
}


def competing_hypotheses(project_id: str) -> list[dict]:
    records = [{"hypothesis_id": category.lower(), "project_id": project_id,
        "category": category, "statement": _EXPLANATIONS[category][0],
        "falsification_test": _EXPLANATIONS[category][1], "status": "UNRESOLVED",
        "evidence_ids": []} for category in CATEGORIES]
    for record in records:
        validate_record("hypothesis", record)
    return records


def evaluate(hypothesis: dict, evidence: list[dict]) -> dict:
    """Evidence links are caller assertions, not proof of causality or truth.

    Mixed signals stay unresolved. Support alone cannot create a verified
    conclusion. Prior rejection cannot disappear merely because a run passed.
    """
    validate_record("hypothesis", hypothesis)
    if type(evidence) is not list:
        raise ContractError("evidence must be an array")
    for record in evidence:
        validate_record("evidence", record)
    evidence_ids = [r["record_id"] for r in evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ContractError("duplicate evidence identity")
    if not set(hypothesis["evidence_ids"]).issubset(evidence_ids):
        raise ContractError("evaluation must retain historical hypothesis evidence")
    result = deepcopy(hypothesis)
    supports, contradicts, related = set(), set(), set()
    for record in evidence:
        validate_record("evidence", record)
        if record["project_id"] != hypothesis["project_id"]:
            raise ContractError("cross-project hypothesis evidence")
        for link in record["hypothesis_links"]:
            if link["hypothesis_id"] == hypothesis["hypothesis_id"]:
                related.add(record["record_id"])
                if link["relation"] == "SUPPORTS":
                    supports.add(record["record_id"])
                elif link["relation"] == "CONTRADICTS":
                    contradicts.add(record["record_id"])
    if supports and contradicts:
        status = "UNRESOLVED"
    elif contradicts:
        status = "REJECTED_HYPOTHESIS"
    elif supports:
        status = "HYPOTHESIS"
    else:
        status = "UNRESOLVED"
    if not set(hypothesis["evidence_ids"]).issubset(related):
        raise ContractError("evaluation cannot drop historical hypothesis relationships")
    result.update(status=status, evidence_ids=sorted(related))
    return result
