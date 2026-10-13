# Roadmap

The target is an agent-neutral engineering strategy engine with measurable
benefit. Milestones are FOX-specific; CAE's M0-M7 is not a mandatory template.

The table defines work and acceptance targets, not a claim that every target has
passed. The authoritative dated status is
[SESSION_CHECKPOINT.json](docs/continuity/SESSION_CHECKPOINT.json), with supporting
results in [TEST_EVIDENCE.md](docs/continuity/TEST_EVIDENCE.md).

| Phase | Work | Acceptance target |
| --- | --- | --- |
| 0 | Repository and mission foundation | Independent project, MIT license, scope and continuity documented |
| 1 | Typed records and schemas | Strict runtime validation and schema parity for valid and invalid fixtures |
| 2 | Deterministic hypothesis and decision engine | Reproducible decisions, evidence-linked revision, unresolved contradictions |
| 3 | Strategy registry | Eight independent tactics and extension without core edits |
| 4 | Architecture discovery | Competing revisable candidates with every required comparison dimension |
| 5 | Authority shield | Default denial for execution; scoped path/resource/lifetime checks and adversarial tests |
| 6 | Agent adapters | SDK and JSON lines contract; each external agent verified separately |
| 7 | Adversarial validation | Synthetic examples, malformed input, contradictions, and environment/software alternatives |
| 8 | Quality and publication | Tests, staged-tree safety review, dependency provenance, confirmed remote checkpoint |

`DESIGNED` means the interface or behavior is specified. `IMPLEMENTED` means code
exists. `TESTED` means a recorded test exercised it. `VERIFIED` means the named
acceptance claim is supported within an explicit scope. `BLOCKED` names a specific
dependency preventing progress. No label implies production readiness.

After the concept foundation, priorities are stronger journal recovery and
concurrency semantics, hostile-filesystem authority evaluation, bounded adapter
inputs, real agent integration checks, and reproducible comparative benchmarks.
An MCP adapter requires a versioned protocol design and conformance validation.
Any model integration must leave deterministic offline use intact.

Benchmark work must compare equivalent tasks, budgets, tools, and acceptance
criteria for agents with and without FOX. Publish unsuccessful results and
uncertainty as well as favorable results. Do not claim engineering improvements
before this evidence exists.
