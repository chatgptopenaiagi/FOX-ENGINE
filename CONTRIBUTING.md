# Contributing

Start with [AGENTS.md](AGENTS.md) and the continuity checkpoint. Keep work scoped
to FOX. Do not inspect sibling projects, agent credentials, private reasoning
traces, or unrelated runtime state. Use synthetic fixtures with clear provenance.

A useful change states the engineering problem, the assumption it challenges,
its observable result, and its remaining limits. Preserve failed experiments
alongside later corrections. A failure that no longer reproduces is unresolved
until evidence supports an explanation.

Runtime behavior must remain deterministic and usable offline. New strategy
definitions should use the registry contract instead of adding animal-specific
branches to the core. Contract changes require matching schema, runtime
validation, documentation, examples, and compatibility tests. Avoid dependencies
without a concrete need and a recorded license/provenance review.

Before submitting a checkpoint:

1. Inspect Git status and preserve unrelated or pre-existing files.
2. Run `python -m unittest discover -s tests -v` with `PYTHONPATH=src`.
3. Run schema parity validation when development dependencies are available.
4. Record actual results and limitations in the continuity records.
5. Review every staged file for secrets, personal data, unauthorized material,
   and dependency/license provenance.

Use the labels `DESIGNED`, `IMPLEMENTED`, `TESTED`, `VERIFIED`, and `BLOCKED`
precisely. A verification statement must name its scope and evidence. Do not
claim that an adapter works with a particular agent without testing that agent.

Pull requests should explain the final behavior and relevant validation, not
recount exploratory conversation. Include regression coverage when a bug could
weaken validation, evidence preservation, or authority boundaries.

Contributions are offered under the repository's MIT license. Preserve third-party
license notices when adding authorized material. Security defaults are not
additional license conditions.
