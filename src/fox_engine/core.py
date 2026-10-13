"""Pure deterministic strategy recommendations with explicit revision lineage."""
from __future__ import annotations
from copy import deepcopy
from fox_engine.contracts import (
    CONTRACT_VERSION, PRINCIPLES, ContractError, EngineeringProblem, EvidenceRecord,
    content_hash, validate_record,
)
from fox_engine.hypotheses import competing_hypotheses, evaluate
from fox_engine.strategies import StrategyRegistry


def verify_decision(decision: dict) -> None:
    validate_record("decision", decision)
    body = {key: value for key, value in decision.items() if key != "decision_id"}
    if decision["decision_id"] != "decision:" + content_hash(body):
        raise ContractError("decision content digest mismatch")
    if any(decision[key] != decision["problem"][key] for key in ("project_id", "problem_id", "domain")):
        raise ContractError("decision problem snapshot mismatch")
    if set(decision["evidence_ids"]) != set(decision["evidence_hashes"]):
        raise ContractError("decision evidence index mismatch")
    ids = [h["hypothesis_id"] for h in decision["hypotheses"]]
    if len(ids) != len(set(ids)):
        raise ContractError("duplicate hypothesis identity in decision")
    if any(h["project_id"] != decision["project_id"] or not set(h["evidence_ids"]).issubset(decision["evidence_ids"]) for h in decision["hypotheses"]):
        raise ContractError("invalid hypothesis evidence or project in decision")


def _retain_hypotheses(prior: list[dict], current: list[dict]) -> None:
    by_id = {h["hypothesis_id"]: h for h in current}
    for old in prior:
        new = by_id.get(old["hypothesis_id"])
        if new is None:
            raise ContractError("revision cannot remove historical hypotheses")
        if any(new[key] != old[key] for key in ("statement", "category", "falsification_test")):
            raise ContractError("changed hypothesis requires a new identity")
        if not set(old["evidence_ids"]).issubset(new["evidence_ids"]):
            raise ContractError("revision cannot remove historical hypothesis evidence links")


class FoxEngine:
    """SDK entry point. No filesystem, model, network or process side effects."""

    def __init__(self, registry: StrategyRegistry | None = None):
        self.registry = registry if registry is not None else StrategyRegistry()

    def analyze(self, problem: EngineeringProblem, evidence: list[EvidenceRecord] | None = None,
                hypotheses: list[dict] | None = None, previous_decision: dict | None = None) -> dict:
        validate_record("engineering_problem", problem)
        evidence = deepcopy(evidence if evidence is not None else [])
        if type(evidence) is not list:
            raise ContractError("evidence must be an array")
        for record in evidence:
            validate_record("evidence", record)
            if record["project_id"] != problem["project_id"]:
                raise ContractError("cross-project evidence")
        evidence.sort(key=lambda record: record["record_id"])
        ids = [record["record_id"] for record in evidence]
        if len(ids) != len(set(ids)):
            raise ContractError("duplicate evidence identity")
        evidence_hashes = {record["record_id"]: content_hash(record) for record in evidence}
        if previous_decision is not None:
            verify_decision(previous_decision)
            if (previous_decision["project_id"], previous_decision["problem_id"]) != (problem["project_id"], problem["problem_id"]):
                raise ContractError("decision lineage crosses problem or project")
            if any(evidence_hashes.get(key) != value for key, value in previous_decision["evidence_hashes"].items()):
                raise ContractError("revision must retain unchanged historical evidence")
        if hypotheses is None:
            hypotheses = (previous_decision["hypotheses"] if previous_decision else competing_hypotheses(problem["project_id"]))
        if type(hypotheses) is not list or not hypotheses:
            raise ContractError("at least one competing hypothesis is required")
        hypotheses = deepcopy(hypotheses)
        for hypothesis in hypotheses:
            validate_record("hypothesis", hypothesis)
            if hypothesis["project_id"] != problem["project_id"]:
                raise ContractError("cross-project hypothesis")
        hypothesis_ids = [h["hypothesis_id"] for h in hypotheses]
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ContractError("duplicate hypothesis identity")
        if any(link["hypothesis_id"] not in hypothesis_ids for record in evidence for link in record["hypothesis_links"]):
            raise ContractError("evidence references unknown hypothesis")
        if any(eid not in ids for h in hypotheses for eid in h["evidence_ids"]):
            raise ContractError("hypothesis references missing evidence")
        if previous_decision:
            _retain_hypotheses(previous_decision["hypotheses"], hypotheses)
        evaluated = sorted((evaluate(h, evidence) for h in hypotheses), key=lambda h: h["hypothesis_id"])
        unresolved = ["Caller-supplied observations and hypothesis links require independent verification."]
        if not evidence:
            unresolved.append("No observations supplied; recommendations are investigative proposals.")
        if problem["domain"] == "unknown":
            unresolved.append("Problem domain is unknown; obtain an explicit classification before specialist work.")
        statements = [{"kind": "ASSUMPTION", "text": text, "evidence_ids": []} for text in problem["assumptions"]]
        statements += [{"kind": "OBSERVED_FACT", "text": "Reported observation: " + r["observed_condition"],
                        "evidence_ids": [r["record_id"]]} for r in evidence]
        statements += [{"kind": h["status"], "text": h["statement"], "evidence_ids": h["evidence_ids"]} for h in evaluated]
        recommendations = []
        domain = {"recovery": "continuity", "unknown": "general"}.get(problem["domain"], problem["domain"])
        gaps = [] if evidence else ["evidence"]
        if problem["assumptions"]:
            gaps.append("assumptions")
        if any(link["relation"] == "CONTRADICTS" for record in evidence for link in record["hypothesis_links"]):
            gaps.append("contradictions")
        for strategy in self.registry.select(domain, evidence_gaps=gaps):
            actions = [{"action_id": "review:" + content_hash(strategy["strategy_id"]),
                "description": strategy["description"], "operation": "READ_ONLY_ANALYSIS",
                "requires_authorization": False,
                "completion_criteria": "; ".join(strategy["completion_criteria"]), "evidence_ids": ids}]
            if strategy["strategy_id"] in ("FOX", "ANT"):
                actions += [{"action_id": "test:" + content_hash(h["hypothesis_id"]), "description": h["falsification_test"],
                    "operation": "TEST_EXECUTION", "requires_authorization": True,
                    "completion_criteria": "Record one bounded probe and a control with command, exit status and environment; retain both outcomes.",
                    "evidence_ids": h["evidence_ids"]} for h in evaluated]
            rationale = "Applicable to the explicit problem domain and evidence gaps."
            if problem["domain"] == "validation" and strategy["strategy_id"] == "FOX":
                rationale = "VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION: inspect the rejected fixture and valid control before proposing guard changes."
            recommendations.append({"strategy_id": strategy["strategy_id"], "rationale": rationale,
                "expected_outcomes": strategy["expected_outputs"],
                "cost_estimate": {"effort": "MEDIUM" if strategy["strategy_id"] in ("OCTOPUS", "EAGLE", "BEAVER", "WOLF") else "LOW",
                    "basis": "Uncalibrated qualitative planning estimate; not measured time, cost, success rate or probability."},
                "actions": actions})
        statements += [{"kind": "PROPOSAL", "text": r["rationale"], "evidence_ids": ids} for r in recommendations]
        prior_statuses = {h["hypothesis_id"]: h["status"] for h in previous_decision["hypotheses"]} if previous_decision else {}
        revisions = [{"hypothesis_id": h["hypothesis_id"], "previous_status": prior_statuses[h["hypothesis_id"]],
                      "new_status": h["status"], "evidence_ids": h["evidence_ids"]}
                     for h in evaluated if h["hypothesis_id"] in prior_statuses and prior_statuses[h["hypothesis_id"]] != h["status"]]
        # New contradictions prioritize challenge/review; unchanged evidence never causes a revision by itself.
        if revisions:
            recommendations.sort(key=lambda r: (r["strategy_id"] not in ("OWL", "FOX", "ANT"), r["strategy_id"]))
        body = {"contract_version": CONTRACT_VERSION, "project_id": problem["project_id"],
            "problem_id": problem["problem_id"], "domain": problem["domain"], "principles": list(PRINCIPLES),
            "problem": deepcopy(problem),
            "statements": statements, "hypotheses": evaluated, "recommendations": recommendations,
            "evidence_ids": ids, "evidence_digest": content_hash(evidence), "evidence_hashes": evidence_hashes,
            "previous_decision_id": previous_decision["decision_id"] if previous_decision else None,
            "revisions": revisions, "unresolved": unresolved}
        decision = {"decision_id": "decision:" + content_hash(body), **body}
        validate_record("decision", decision)
        return decision

    def reconstruct(self, decisions: list[dict]) -> list[dict]:
        """Return a single complete decision lineage; refuse holes and forks."""
        if not decisions:
            return []
        for decision in decisions:
            verify_decision(decision)
        by_id = {d["decision_id"]: d for d in decisions}
        if len(by_id) != len(decisions):
            raise ContractError("duplicate decision identity")
        if len({(d["project_id"], d["problem_id"]) for d in decisions}) != 1:
            raise ContractError("mixed decision lineages")
        ordered, parent = [], None
        while len(ordered) < len(decisions):
            children = [d for d in decisions if d["previous_decision_id"] == parent]
            if len(children) != 1 or children[0] in ordered:
                raise ContractError("incomplete, cyclic or forked lineage")
            child = children[0]
            if ordered and any(child["evidence_hashes"].get(k) != v for k, v in ordered[-1]["evidence_hashes"].items()):
                raise ContractError("historical evidence changed in lineage")
            if ordered:
                _retain_hypotheses(ordered[-1]["hypotheses"], child["hypotheses"])
            ordered.append(child)
            parent = child["decision_id"]
        return deepcopy(ordered)
