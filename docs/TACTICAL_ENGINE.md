# Tactical decision engine

The concept engine consumes a validated problem, relevant evidence, optional
hypotheses, and an optional prior decision. It produces structured recommendations
and explicit uncertainty through deterministic rules.

The Python entry point is:

```python
from fox_engine import FoxEngine

engine = FoxEngine()
decision = engine.analyze(
    problem,
    evidence=None,
    hypotheses=None,
    previous_decision=None,
)
```

Here `problem` is a record satisfying
[`engineering_problem.schema.json`](../schemas/engineering_problem.schema.json).
Evidence and hypotheses must satisfy their corresponding schemas. Do not pass a
natural-language prompt where a structured record is required.

Required problem fields are `problem_id`, `project_id`, `description`, `domain`,
`assumptions`, `constraints`, and `desired_outcome`. Assumptions and constraints
are lists of strings. Domains are `unknown`, `validation`, `environment`,
`software`, `architecture`, `coordination`, `recovery`, `dependency`, or
`requirements`. The explicit domain is host-supplied context, not independent
causal verification by FOX.

Omitting evidence supplies an empty observation set. Omitting hypotheses creates
the eight competing failure explanations (or retains the prior decision's
hypotheses for a revision). An explicitly empty hypothesis list is invalid.

The workflow identifies the supplied domain, evidence, assumptions, and gaps;
selects applicable registry tactics; presents expected outputs and qualitative
effort estimates for comparison; proposes investigations; evaluates explicit hypothesis relationships;
and creates a decision record. Arbitrary semantic understanding remains the
host agent's responsibility.

## Epistemic status

| Status | Meaning |
| --- | --- |
| `OBSERVED_FACT` | An observation from a named source, within its stated scope |
| `HYPOTHESIS` | A testable explanation that has not been established |
| `ASSUMPTION` | A premise currently used without adequate verification |
| `PROPOSAL` | An action or architecture offered for consideration |
| `REJECTED_HYPOTHESIS` | An explanation rejected for a recorded evidential reason |
| `VERIFIED_CONCLUSION` | A bounded proposition supported by the stated verification |
| `UNRESOLVED` | Missing, conflicting, or insufficient evidence prevents a conclusion |

Confidence qualification is descriptive. It is not an empirically calibrated
probability. A missing observation must not be manufactured; conflicting evidence
must remain visible even when one interpretation appears more plausible.
Supporting evidence alone leaves a hypothesis as `HYPOTHESIS`; explicit
contradicting evidence can reject its current scope, and mixed support and
contradiction produce `UNRESOLVED`. The engine must not promote a supported
explanation to a verified causal conclusion merely by counting records.

Revision creates a new decision linked to its predecessor. Evidence supporting
revision must be retained, and identical validated inputs should produce identical
analysis output. A strategy is not changed merely to make a failing test pass.

Supply every historical evidence record unchanged when passing `previous_decision`.
Omitting or changing a prior record is rejected. Retain prior hypotheses too: a
changed statement, category, or falsification test requires a new hypothesis
identity rather than silently changing the meaning of an existing one.

`FoxEngine.reconstruct(decisions)` verifies decision digests and returns one
complete predecessor chain, rejecting missing links, forks, mixed projects, and
changed historical evidence. Hypothesis evaluation is the module function
`fox_engine.hypotheses.evaluate(hypothesis, evidence)`; it is not a `FoxEngine`
method. `fox_engine.core.verify_decision(decision)` checks the record structure
and its content digest, not the truth of its conclusions.

The generic adapter accepts a JSON line with `contract_version: "1.0"`, a
`request_id`, `operation: "analyze"`, and a `payload` containing `problem` and
optional analysis inputs. See [AGENT_COMPATIBILITY.md](AGENT_COMPATIBILITY.md).
