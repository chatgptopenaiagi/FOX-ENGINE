# FOX ENGINE

**Falsification-Oriented eXploration** is an agent-neutral engineering strategy
engine. It helps a host agent record assumptions, compare explanations for
failures, preserve contradictory evidence, and revise its recommendations.

> FOX does not exist to prove that an AI agent is correct. FOX exists to help
> the agent discover when it is wrong, understand why, and choose a better
> course of action.

This is the **0.1.0-concept** foundation, distributed as Python version
`0.1.0.dev0`. It is an experimental deterministic tool, not a production-ready
agent, a replacement language model, or proof of improved engineering outcomes.
It runs offline without a model provider and does not execute its recommendations.

## What the foundation covers

- Versioned JSON contracts for problems, strategies, hypotheses, decisions,
  evidence, and authority.
- Eight independently registered tactics: OWL, FOX, WOLF, OCTOPUS, TORTOISE,
  EAGLE, ANT, and BEAVER.
- Deterministic analysis, explicit uncertainty, falsification planning, and
  evidence-linked decision revision.
- Revisable architecture candidates with comparison criteria.
- Append-oriented evidence preservation and separate integrity checking.
- Scoped authority checks that do not replace the host's permission system.
- A Python SDK and JSON lines over standard input/output.

The five principles are executable requirements. See
[the principle-to-interface map](docs/PHILOSOPHY.md) and the
[architecture](ARCHITECTURE.md). Actual validation results, unresolved work, and
the next eligible task are recorded in [continuity](docs/continuity/).

## Run locally

Use Python 3.11 or newer. Runtime code uses the Python standard library.
From the repository root, in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
'{"contract_version":"1.0","request_id":"registry-demo","operation":"strategies","payload":{}}' | python -m fox_engine
```

The equivalent POSIX invocation is:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
printf '%s\n' '{"contract_version":"1.0","request_id":"registry-demo","operation":"strategies","payload":{}}' | PYTHONPATH=src python -m fox_engine
```

The SDK accepts structured records:

```python
from fox_engine import FoxEngine

problem = {
    "problem_id": "synthetic-validator-review",
    "project_id": "example",
    "description": "A validator rejected a synthetic diagnostic record.",
    "domain": "validation",
    "assumptions": ["The rejected input satisfies the documented contract."],
    "constraints": ["Preserve the validator rule and original failure."],
    "desired_outcome": "Distinguish invalid input from a validator defect.",
}
decision = FoxEngine().analyze(problem)
```

See [the tactical contract](docs/TACTICAL_ENGINE.md),
[agent integration](docs/AGENT_COMPATIBILITY.md), and [examples](examples/).

## Boundaries

FOX records observable decisions and evidence summaries, never hidden model
reasoning. A recommendation grants no filesystem, process, network, or GitHub
authority. The authority checker is a policy component, not an operating-system
sandbox. Local hashes can reveal some changes but do not make evidence immutable.

The CAE example is an authorized account supplied by the project initiator;
FOX's fixtures are synthetic and do not independently verify that external
experiment. No CAE files, configuration, credentials, or runtime state are used.
See [the case study](docs/CAE_CASE_STUDY.md) and [limitations](docs/LIMITATIONS.md).

Codex, Claude, Gemini, Qwen, and other agents are compatibility targets.
Compatibility is not established merely because an agent can exchange JSON.
[The compatibility matrix](docs/AGENT_COMPATIBILITY.md) separates designed
integration from verified integration. No HTTP listener is enabled.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md), [AGENTS.md](AGENTS.md), and
[SECURITY.md](SECURITY.md). FOX is licensed under [MIT](LICENSE). Runtime security
defaults are engineering choices; they do not add restrictions to the MIT grant.
