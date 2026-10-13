"""Data-only engineering strategies; importing a module never runs a tactic."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Iterable, Mapping
from typing import Any


def _strategy(
    strategy_id: str,
    description: str,
    domains: list[str],
    inputs: list[str],
    outputs: list[str],
    evidence: list[str],
    failures: list[str],
    completion: list[str],
) -> dict[str, Any]:
    return {
        "strategy_id": strategy_id,
        "description": description,
        "applicability_conditions": domains,
        "required_inputs": inputs,
        "expected_outputs": outputs,
        "risk_level": "LOW",
        "authorization_requirements": ["READ_ONLY_ANALYSIS"],
        "evidence_requirements": evidence,
        "failure_conditions": failures,
        "completion_criteria": completion,
    }


_BUILTINS = (
    _strategy(
        "OWL", "Observe evidence and reconstruct previous decisions.",
        ["general", "evidence", "history"],
        ["problem description", "available decision and evidence records"],
        ["chronological decision summary", "evidence gaps"],
        ["Cite record IDs; mark absent history UNRESOLVED."],
        ["Untraceable source", "Historical failure silently replaced by a pass"],
        ["Every reported observation cites a source or is marked unresolved."],
    ),
    _strategy(
        "FOX", "Challenge assumptions with competing falsifiable explanations.",
        ["failure", "validation", "software", "environment", "dependency", "requirements", "assumptions", "contradictions"],
        ["observed failure", "requirements and validator contract"],
        ["competing hypotheses", "bounded discriminating test proposals"],
        ["Check validator correctness before proposing validator modification."],
        ["Passing test obtained solely by weakening a guard", "Non-reproduction called a solution"],
        ["Each explanation has a discriminating test and unresolved claims remain explicit."],
    ),
    _strategy(
        "WOLF", "Analyze task dependencies and coordinate bounded engineering work.",
        ["coordination", "dependency", "dependencies"],
        ["task descriptions", "dependency constraints", "resource constraints"],
        ["dependency graph", "parallelism and handoff plan"],
        ["Document prerequisite evidence for each dependent task."],
        ["Dependency cycle unexplained", "Task ownership or acceptance condition absent"],
        ["Every task has inputs, an owner role, and an observable completion condition."],
    ),
    _strategy(
        "OCTOPUS", "Explore competing revisable software architecture proposals.",
        ["architecture", "alternatives"],
        ["human software vision", "constraints and assumptions"],
        ["at least two candidate architectures", "explicit tradeoff comparison"],
        ["Distinguish proposed tradeoffs from measured behavior."],
        ["One template imposed universally", "Unsupported numerical certainty"],
        ["Compare all required dimensions and specify evidence that could reject each candidate."],
    ),
    _strategy(
        "TORTOISE", "Preserve continuity, provenance, contradictions, and recovery plans.",
        ["general", "continuity", "history", "recovery", "contradictions"],
        ["current evidence and decisions", "last checkpoint when available"],
        ["checkpoint proposal", "contradiction inventory", "next executable task"],
        ["Retain failed observations independently from later successful observations."],
        ["Contradictory evidence removed", "Local hashes described as immutable"],
        ["A new session can identify verified work, unresolved claims, and the next task."],
    ),
    _strategy(
        "EAGLE", "Assess global system boundaries and consequences of architectural choices.",
        ["architecture", "security", "deployment"],
        ["candidate architecture", "trust and deployment constraints"],
        ["consequence assessment", "failure and trust boundary questions"],
        ["Trace each consequence to an explicit assumption or observation."],
        ["External acceptance asserted without observation", "Trust boundary unspecified"],
        ["Security, portability, recovery, and resource tradeoffs are explicit."],
    ),
    _strategy(
        "ANT", "Plan bounded verification and preserve regression evidence.",
        ["testing", "verification", "failure", "validation", "environment", "software", "dependency"],
        ["hypotheses", "reproduction procedure", "execution constraints"],
        ["bounded test plan", "expected discriminating observations"],
        ["Record command, environment, exit status, and actual observation for each run."],
        ["Environment and implementation changed in the same uncontrolled experiment"],
        ["Each proposed test varies one discriminating condition and has a stopping bound."],
    ),
    _strategy(
        "BEAVER", "Plan maintainable implementation with explicit acceptance criteria.",
        ["implementation", "construction", "software", "requirements"],
        ["chosen provisional architecture", "acceptance criteria", "constraints"],
        ["bounded implementation plan", "interface and regression checklist"],
        ["Keep unresolved assumptions visible in each dependent implementation step."],
        ["Implementation authority inferred from a recommendation", "Unbounded construction task"],
        ["Every proposed change has an interface, acceptance criterion, and recovery approach."],
    ),
)


class StrategyRegistry:
    """An explicit registry with defensive copies and no executable discovery.

    Applicability is a deterministic match against caller-declared domain labels.
    Evidence gaps are labels, not claims inferred by a language model. Results
    are candidates, never execution authority or empirically ranked outcomes.
    """

    def __init__(self, include_builtins: bool = True) -> None:
        self._strategies: dict[str, dict[str, Any]] = {}
        if include_builtins:
            for strategy in _BUILTINS:
                self.register(strategy)

    def register(self, strategy: Mapping[str, Any]) -> None:
        """Add a validated data record. Existing IDs cannot be overwritten."""
        from fox_engine.contracts import validate_record

        if not isinstance(strategy, Mapping):
            raise ValueError("strategy must be a mapping")
        record = deepcopy(dict(strategy))
        validate_record("strategy", record)
        strategy_id = record["strategy_id"]
        if strategy_id in self._strategies:
            raise ValueError(f"strategy already registered: {strategy_id}")
        self._strategies[strategy_id] = record

    def get(self, strategy_id: str) -> dict[str, Any]:
        """Return an independent copy or raise KeyError for an unknown ID."""
        return deepcopy(self._strategies[strategy_id])

    def list(self) -> list[dict[str, Any]]:
        """Return independent records sorted by stable strategy identity."""
        return [self.get(key) for key in sorted(self._strategies)]

    def select(
        self, domain: str, evidence_gaps: Iterable[str] = ()
    ) -> list[dict[str, Any]]:
        """Match domain/gap labels, preferring gap matches then sorting by ID.

        ``general`` applies to every domain. Unknown domains retain only general
        and explicitly gap-matched strategies; missing evidence is not invented.
        """
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")
        if isinstance(evidence_gaps, (str, bytes)):
            raise ValueError("evidence_gaps must be an iterable of labels")
        gaps = list(evidence_gaps)
        if any(not isinstance(gap, str) or not gap.strip() for gap in gaps):
            raise ValueError("evidence gaps must be non-empty strings")
        gap_labels = {gap.strip().lower() for gap in gaps}
        labels = gap_labels | {domain.strip().lower(), "general"}
        candidates = [
            record for record in self.list()
            if labels.intersection(record["applicability_conditions"])
        ]
        return sorted(
            candidates,
            key=lambda record: (
                not bool(gap_labels.intersection(record["applicability_conditions"])),
                record["strategy_id"],
            ),
        )


__all__ = ["StrategyRegistry"]
