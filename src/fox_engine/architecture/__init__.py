"""Deterministic architecture exploration templates, not autonomous invention."""

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any


COMPARISON_DIMENSIONS = (
    "complexity", "reliability", "security", "maintainability", "portability",
    "testability", "resource_requirements", "expected_failure_behavior",
)

_LIST_FIELDS = (
    "assumptions", "system_boundaries", "security_boundaries", "failure_models",
    "testing_strategy", "deployment_strategy", "recovery_mechanisms",
    "acceptance_criteria",
)


def _text(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _texts(value: Any, field: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    for item in value:
        _text(item, field)


def validate_candidate(candidate: Mapping[str, Any]) -> None:
    """Reject incomplete comparisons, broken component references, and certainty.

    This validates structural completeness only. It does not verify that a
    proposed architecture satisfies its vision or that its tradeoffs are true.
    """
    if not isinstance(candidate, Mapping):
        raise ValueError("architecture candidate must be a mapping")
    for field in ("architecture_id", "name"):
        _text(candidate.get(field), field)
    if candidate.get("epistemic_status") != "PROPOSAL":
        raise ValueError("candidate epistemic_status must be PROPOSAL")
    if candidate.get("revisable") is not True:
        raise ValueError("architecture proposals must remain revisable")
    for field in _LIST_FIELDS:
        _texts(candidate.get(field), field)
    comparisons = candidate.get("comparison")
    if not isinstance(comparisons, Mapping) or set(comparisons) != set(COMPARISON_DIMENSIONS):
        raise ValueError("comparison must include exactly all eight comparison dimensions")
    for dimension in COMPARISON_DIMENSIONS:
        _text(comparisons[dimension], f"comparison.{dimension}")
    components = candidate.get("components")
    if not isinstance(components, list) or not components:
        raise ValueError("components must be a non-empty list")
    component_ids: set[str] = set()
    for component in components:
        if not isinstance(component, Mapping):
            raise ValueError("component must be a mapping")
        identity = component.get("component_id")
        _text(identity, "component_id")
        if identity in component_ids:
            raise ValueError("component IDs must be unique")
        component_ids.add(identity)
        _texts(component.get("responsibilities"), "responsibilities")
    interfaces = candidate.get("interfaces")
    dependencies = candidate.get("dependencies")
    if not isinstance(interfaces, list) or not isinstance(dependencies, list):
        raise ValueError("interfaces and dependencies must be lists")
    interface_ids: set[str] = set()
    for edge in interfaces + dependencies:
        if not isinstance(edge, Mapping):
            raise ValueError("interface or dependency must be a mapping")
        for endpoint in ("from_component", "to_component"):
            if not isinstance(edge.get(endpoint), str) or edge[endpoint] not in component_ids:
                raise ValueError(f"{endpoint} must reference a declared component")
    for interface in interfaces:
        identity = interface.get("interface_id")
        _text(identity, "interface_id")
        _text(interface.get("contract"), "interface contract")
        if identity in interface_ids:
            raise ValueError("interface IDs must be unique")
        interface_ids.add(identity)


def _templates() -> list[dict[str, Any]]:
    shared = {
        "epistemic_status": "PROPOSAL",
        "revisable": True,
        "assumptions": [
            "The vision can be decomposed into application policy and an external-system boundary.",
            "Latency, throughput, deployment constraints, and external acceptance remain unmeasured.",
        ],
        "testing_strategy": [
            "Test each boundary contract using synthetic valid and invalid inputs.",
            "Inject boundary failures and preserve both failed and successful observations.",
            "Compare identical bounded workloads before selecting a candidate.",
        ],
        "acceptance_criteria": [
            "Translate the supplied vision into observable functional requirements before implementation.",
            "Reject malformed requests without changing the validation contract.",
            "Demonstrate recovery after an injected boundary failure in a bounded test.",
        ],
    }
    monolith = deepcopy(shared)
    monolith.update({
        "architecture_id": "modular_local",
        "name": "Modular local application",
        "system_boundaries": ["One application process with explicit internal module interfaces."],
        "components": [
            {"component_id": "application", "responsibilities": ["Validate requests and implement domain policy."]},
            {"component_id": "gateway", "responsibilities": ["Adapt external systems behind a narrow interface."]},
        ],
        "interfaces": [{
            "interface_id": "gateway_contract", "from_component": "application",
            "to_component": "gateway", "contract": "Explicit typed request/result boundary with failure results.",
        }],
        "dependencies": [{"from_component": "application", "to_component": "gateway"}],
        "security_boundaries": [
            "Validate input at the gateway; internal modules share process authority.",
            "Host approval is required for effects; module boundaries are not an OS sandbox.",
        ],
        "failure_models": ["A fatal gateway fault can terminate the shared process."],
        "deployment_strategy": ["Package a single local application; measure target platform support."],
        "recovery_mechanisms": ["Checkpoint durable work and restart with an explicit recovery procedure."],
        "comparison": {
            "complexity": "Hypothesis: one process reduces deployment coordination; module discipline is still required.",
            "reliability": "Hypothesis: fewer interprocess failures, but shared-process crash propagation.",
            "security": "Shared process authority; permission checks must occur at every effect boundary.",
            "maintainability": "Hypothesis: typed module boundaries support change until coupling grows.",
            "portability": "Hypothesis: one package simplifies installation; native dependencies remain unknown.",
            "testability": "Contract and fault-injection tests can run in process; isolation must be tested separately.",
            "resource_requirements": "Hypothesis: lower process overhead; workload memory and CPU require measurement.",
            "expected_failure_behavior": "A process crash may stop all work; checkpoint recovery requires verification.",
        },
    })
    workers = deepcopy(shared)
    workers.update({
        "architecture_id": "isolated_worker",
        "name": "Coordinator with a bounded worker",
        "system_boundaries": ["Separate coordinator and worker processes connected through versioned local messages."],
        "components": [
            {"component_id": "coordinator", "responsibilities": ["Validate requests, record outcomes, and coordinate bounded work."]},
            {"component_id": "worker", "responsibilities": ["Handle external-system adaptation within host-enforced permissions."]},
        ],
        "interfaces": [{
            "interface_id": "worker_protocol", "from_component": "coordinator",
            "to_component": "worker", "contract": "Versioned request/result messages, correlation IDs, bounded timeouts.",
        }],
        "dependencies": [{"from_component": "coordinator", "to_component": "worker"}],
        "security_boundaries": [
            "Separate process identity alone grants no sandbox guarantee.",
            "Propose least-privilege worker permissions enforced and verified by the host.",
            "Keep transport local; network exposure requires separate explicit authorization.",
        ],
        "failure_models": ["Worker crash, lost response, duplicate request, cancellation race, or coordinator failure."],
        "deployment_strategy": ["Package coordinated local processes with a documented protocol compatibility policy."],
        "recovery_mechanisms": ["Record request identity, bound retries, and reconcile uncertain outcomes before repeating effects."],
        "comparison": {
            "complexity": "Hypothesis: protocol evolution and lifecycle coordination add implementation work.",
            "reliability": "Hypothesis: worker failures can be contained; transport and coordinator failures are added.",
            "security": "Host-enforced reduced worker authority is possible; process separation alone is insufficient.",
            "maintainability": "Hypothesis: replaceable workers help separation at the cost of protocol compatibility work.",
            "portability": "Hypothesis: process lifecycle and permission differences require platform-specific verification.",
            "testability": "Protocol replay, timeout, cancellation, and crash-recovery tests are required.",
            "resource_requirements": "Hypothesis: extra processes and serialization add overhead; measure before selection.",
            "expected_failure_behavior": "Worker outcomes may be uncertain after timeouts; reconcile before retrying effects.",
        },
    })
    return [monolith, workers]


def discover_architectures(
    vision: str, candidates: Sequence[Mapping[str, Any]] | None = None
) -> dict[str, Any]:
    """Return at least two structurally complete, revisable alternatives.

    Without caller candidates this scaffolds generic deterministic templates.
    The supplied vision is preserved, not claimed to be semantically understood.
    Host agents can submit their own domain-specific competing structures.
    """
    _text(vision, "vision")
    if candidates is None:
        alternatives = _templates()
        method = "DETERMINISTIC_TEMPLATES"
    else:
        if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
            raise ValueError("candidates must be a sequence of mappings")
        if any(not isinstance(candidate, Mapping) for candidate in candidates):
            raise ValueError("candidate must be a mapping")
        alternatives = [deepcopy(dict(candidate)) for candidate in candidates]
        method = "CALLER_PROPOSALS"
    if len(alternatives) < 2:
        raise ValueError("architecture discovery requires at least two competing candidates")
    identities: set[str] = set()
    for candidate in alternatives:
        validate_candidate(candidate)
        identity = candidate["architecture_id"]
        if identity in identities:
            raise ValueError("architecture IDs must be unique")
        identities.add(identity)
    return {
        "epistemic_status": "PROPOSAL",
        "vision": vision,
        "generation_method": method,
        "candidates": alternatives,
        "comparison_dimensions": list(COMPARISON_DIMENSIONS),
        "unresolved_questions": [
            "Which observable acceptance criteria faithfully represent the vision?",
            "Which deployment, security, resource, and latency constraints are mandatory?",
            "Which bounded experiment could reject each candidate architecture?",
            "What new evidence would justify revising the selected provisional structure?",
        ],
        "verification_scope": "Structural completeness only; suitability and tradeoffs remain unverified.",
        "execution_authority": "NONE",
    }


__all__ = ["COMPARISON_DIMENSIONS", "discover_architectures", "validate_candidate"]
