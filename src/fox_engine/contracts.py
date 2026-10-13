"""FOX's closed JSON contracts and a deliberately small offline validator.

Only the vocabulary used by SCHEMAS is supported; this is not a general JSON
Schema implementation. Exported schemas are independently checked in development.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
import re
from typing import Any, Literal, TypedDict

CONTRACT_VERSION = "1.0"
PRINCIPLES = (
    "RECONSTRUCT_DECISIONS", "CHALLENGE_ASSUMPTIONS",
    "DISTINGUISH_FAILURE_ORIGINS", "PRESERVE_CONTRADICTIONS",
    "REVISE_FROM_OBSERVATIONS",
)
KINDS = ["OBSERVED_FACT", "HYPOTHESIS", "ASSUMPTION", "PROPOSAL",
         "REJECTED_HYPOTHESIS", "VERIFIED_CONCLUSION", "UNRESOLVED"]
CATEGORIES = ["IMPLEMENTATION_DEFECT", "INVALID_INPUT", "CORRECT_VALIDATOR",
              "INCORRECT_TEST", "INCOMPATIBLE_ENVIRONMENT", "DEPENDENCY_BEHAVIOR",
              "INCOMPLETE_EVIDENCE", "INCONSISTENT_REQUIREMENT"]
STATUSES = ["HYPOTHESIS", "REJECTED_HYPOTHESIS", "VERIFIED_CONCLUSION", "UNRESOLVED"]
DOMAINS = ["unknown", "validation", "environment", "software", "architecture",
           "coordination", "recovery", "dependency", "requirements"]


class EngineeringProblem(TypedDict):
    problem_id: str
    project_id: str
    description: str
    domain: str
    assumptions: list[str]
    constraints: list[str]
    desired_outcome: str


class HypothesisLink(TypedDict):
    hypothesis_id: str
    relation: Literal["SUPPORTS", "CONTRADICTS", "CONTEXT"]


class EvidenceRecord(TypedDict):
    record_id: str
    project_id: str
    timestamp: str
    observed_condition: str
    source: str
    tool_id: str
    artifact_hashes: dict[str, str]
    command_summary: str
    exit_status: int | None
    hypothesis_links: list[HypothesisLink]
    decision_ids: list[str]
    confidence_qualification: str
    environment: dict[str, str]
    reproduction_steps: list[str]


class StrategyRecord(TypedDict):
    strategy_id: str
    description: str
    applicability_conditions: list[str]
    required_inputs: list[str]
    expected_outputs: list[str]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    authorization_requirements: list[str]
    evidence_requirements: list[str]
    failure_conditions: list[str]
    completion_criteria: list[str]


class ContractError(ValueError):
    """A record is structurally or semantically invalid."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("duplicate JSON key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise ContractError("non-finite JSON number")


def parse_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)


def _obj(properties: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


def _array(items: dict, minimum: int = 0, unique: bool = False) -> dict:
    return {"type": "array", "items": items, "minItems": minimum, "uniqueItems": unique}


TEXT = {"type": "string", "minLength": 1}
STRING = {"type": "string"}
IDENTITY = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"}
TEXTS = _array(TEXT, unique=True)
IDS = _array(IDENTITY, unique=True)
TIMESTAMP = {"type": "string", "format": "date-time",
             "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"}
PROBLEM = _obj({"problem_id": IDENTITY, "project_id": IDENTITY,
                "description": TEXT, "domain": {"enum": DOMAINS},
                "assumptions": TEXTS, "constraints": TEXTS, "desired_outcome": TEXT})
STRATEGY = _obj({"strategy_id": IDENTITY, "description": TEXT,
                 **{key: _array(TEXT, 1, unique=True) for key in ["applicability_conditions", "required_inputs", "expected_outputs",
                                           "authorization_requirements", "evidence_requirements",
                                           "failure_conditions", "completion_criteria"]},
                 "risk_level": {"enum": ["LOW", "MEDIUM", "HIGH"]}})
HYPOTHESIS = _obj({"hypothesis_id": IDENTITY, "project_id": IDENTITY, "statement": TEXT,
                   "category": {"enum": CATEGORIES}, "status": {"enum": STATUSES},
                   "evidence_ids": IDS, "falsification_test": TEXT})
EVIDENCE = _obj({"record_id": IDENTITY, "project_id": IDENTITY, "timestamp": TIMESTAMP,
                 "observed_condition": TEXT, "source": TEXT, "tool_id": TEXT,
                 "artifact_hashes": {"type": "object", "additionalProperties": {
                     "type": "string", "pattern": "^[0-9a-f]{64}$"}},
                 "command_summary": STRING, "exit_status": {"type": ["integer", "null"]},
                 "hypothesis_links": _array(_obj({"hypothesis_id": IDENTITY,
                     "relation": {"enum": ["SUPPORTS", "CONTRADICTS", "CONTEXT"]}}), unique=True),
                 "decision_ids": IDS, "confidence_qualification": TEXT,
                 "environment": {"type": "object", "additionalProperties": STRING},
                 "reproduction_steps": _array(TEXT, minimum=1)})
ACTION = _obj({"action_id": IDENTITY, "description": TEXT,
               "operation": {"enum": ["READ_ONLY_ANALYSIS", "TEST_EXECUTION"]},
               "requires_authorization": {"type": "boolean"},
               "completion_criteria": TEXT, "evidence_ids": IDS})
ACTION["oneOf"] = [
    {"properties": {"operation": {"const": "TEST_EXECUTION"}, "requires_authorization": {"const": True}}},
    {"properties": {"operation": {"const": "READ_ONLY_ANALYSIS"}, "requires_authorization": {"const": False}}},
]
RECOMMENDATION = _obj({"strategy_id": IDENTITY, "rationale": TEXT,
    "expected_outcomes": TEXTS,
    "cost_estimate": _obj({"effort": {"enum": ["LOW", "MEDIUM", "HIGH"]}, "basis": TEXT}),
    "actions": _array(ACTION, 1)})
DECISION = _obj({"contract_version": {"const": CONTRACT_VERSION}, "decision_id": IDENTITY,
    "project_id": IDENTITY, "problem_id": IDENTITY, "domain": {"enum": DOMAINS},
    "problem": PROBLEM,
    "principles": {"const": list(PRINCIPLES)},
    "statements": _array(_obj({"kind": {"enum": KINDS}, "text": TEXT, "evidence_ids": IDS})),
    "hypotheses": _array(HYPOTHESIS), "recommendations": _array(RECOMMENDATION),
    "evidence_ids": IDS, "evidence_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "evidence_hashes": {"type": "object", "additionalProperties": {"type": "string", "pattern": "^[0-9a-f]{64}$"}},
    "previous_decision_id": {"type": ["string", "null"]},
    "revisions": _array(_obj({"hypothesis_id": IDENTITY, "previous_status": {"enum": STATUSES},
        "new_status": {"enum": STATUSES}, "evidence_ids": IDS})), "unresolved": TEXTS})
AUTHORITY_OPERATIONS = ["ANALYZE", "READ_EVIDENCE", "WRITE_EVIDENCE", "CREATE_FILE", "MODIFY_FILE",
    "EXECUTE_TEST", "CREATE_PROCESS", "INSTALL_DEPENDENCY", "READ_CREDENTIALS", "DELETE",
    "MODIFY_SECURITY", "ADMINISTER_ACCOUNT", "PRIVILEGED_COMMAND", "EXPOSE_NETWORK", "PUBLISH",
    "MODIFY_PROTECTED_INSTALLATION"]
AUTHORITY = _obj({"grant_id": IDENTITY, "operation": {"enum": AUTHORITY_OPERATIONS}, "path": TEXT, "resource": TEXT,
                  "not_before": TIMESTAMP, "expires_at": TIMESTAMP})
REQUEST = _obj({"contract_version": {"const": CONTRACT_VERSION}, "request_id": IDENTITY,
    "operation": {"enum": ["analyze", "strategies", "discover_architecture", "verify_evidence"]},
    "payload": {"type": "object"}})
REQUEST["oneOf"] = [{"properties": {"operation": {"const": operation}, "payload": schema}}
    for operation, schema in {
        "analyze": _obj({"problem": PROBLEM, "evidence": _array(EVIDENCE),
            "hypotheses": _array(HYPOTHESIS, 1), "previous_decision": DECISION}, ["problem"]),
        "strategies": _obj({}),
        "discover_architecture": _obj({"vision": TEXT, "candidates": _array({"type": "object"}, 2)}, ["vision"]),
        "verify_evidence": _obj({"records": _array(EVIDENCE)}),
    }.items()]
RESPONSE = _obj({"contract_version": {"const": CONTRACT_VERSION},
    "request_id": {"type": ["string", "null"]}, "ok": {"type": "boolean"},
    "result": {"type": ["object", "array", "null"]},
    "error": {"type": ["object", "null"]}})
RESPONSE["oneOf"] = [
    {"properties": {"ok": {"const": True}, "error": {"type": "null"}, "result": {"type": ["object", "array"]}}},
    {"properties": {"ok": {"const": False}, "result": {"type": "null"}, "error": _obj({
        "code": {"const": "INVALID_REQUEST"}, "message": TEXT})}},
]

SCHEMAS = {name: {"$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": f"https://github.com/chatgptopenaiagi/FOX-ENGINE/schemas/{name}.schema.json",
    "title": f"FOX {name} contract {CONTRACT_VERSION}", **deepcopy(schema)}
    for name, schema in {"engineering_problem": PROBLEM, "strategy": STRATEGY,
        "hypothesis": HYPOTHESIS, "decision": DECISION, "evidence": EVIDENCE,
        "authority": AUTHORITY, "request": REQUEST, "response": RESPONSE}.items()}


def _json_value(value: Any, depth: int = 0) -> None:
    if depth > 64:
        raise ContractError("JSON nesting limit exceeded")
    if type(value) in (str, int, bool, type(None)):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_value(item, depth + 1)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_value(item, depth + 1)
        return
    raise ContractError("value must be finite JSON data")


def _validate(schema: dict, value: Any, path: str) -> None:
    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                _validate(option, value, path)
                matches += 1
            except ContractError:
                pass
        if matches != 1:
            raise ContractError(f"{path}: expected exactly one valid variant")
    if "const" in schema and canonical_json(value) != canonical_json(schema["const"]):
        raise ContractError(f"{path}: unexpected constant")
    if "enum" in schema and not any(canonical_json(value) == canonical_json(x) for x in schema["enum"]):
        raise ContractError(f"{path}: unsupported value")
    types = schema.get("type", [])
    if isinstance(types, str):
        types = [types]
    checks = {"object": type(value) is dict, "array": type(value) is list,
              "string": type(value) is str, "integer": type(value) is int or (type(value) is float and value.is_integer()),
              "boolean": type(value) is bool, "null": value is None}
    if types and not any(checks[t] for t in types):
        raise ContractError(f"{path}: expected {' or '.join(types)}")
    if type(value) is dict:
        props = schema.get("properties", {})
        if set(schema.get("required", [])) - set(value):
            raise ContractError(f"{path}: missing required fields")
        for key, item in value.items():
            if key in props:
                _validate(props[key], item, f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                raise ContractError(f"{path}: unknown fields")
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate(schema["additionalProperties"], item, f"{path}.*")
    if type(value) is list:
        if len(value) < schema.get("minItems", 0):
            raise ContractError(f"{path}: too few items")
        if schema.get("uniqueItems") and len({canonical_json(x) for x in value}) != len(value):
            raise ContractError(f"{path}: duplicate items")
        for index, item in enumerate(value):
            _validate(schema.get("items", {}), item, f"{path}[{index}]")
    if type(value) is str:
        if len(value) < schema.get("minLength", 0):
            raise ContractError(f"{path}: empty value")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise ContractError(f"{path}: invalid string format")
        if schema.get("format") == "date-time":
            try:
                if not value.endswith("Z") and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
                    raise ValueError()
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.utcoffset() is None:
                    raise ValueError()
            except ValueError as exc:
                raise ContractError(f"{path}: invalid timezone-aware timestamp") from exc


def validate_record(name: str, value: Any) -> None:
    if name not in SCHEMAS:
        raise ContractError("unknown contract")
    _json_value(value)
    _validate(SCHEMAS[name], value, name)
