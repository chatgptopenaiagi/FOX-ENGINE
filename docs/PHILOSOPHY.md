# Five executable principles

The five principles are constraints on the implementation, not decorative agent
instructions. Each must be represented in validated data and observable behavior.

| Principle | Interface and record responsibility | Falsifiable contract |
| --- | --- | --- |
| Reconstruct previous decisions | Analysis accepts a previous decision and explicit evidence references | A revision retains its predecessor and does not erase historical claims |
| Challenge assumptions | Problem assumptions, hypotheses, and discriminating test proposals | A claim without adequate evidence remains a hypothesis or unresolved |
| Separate environment from software defects | Competing explanations for implementation, input, validator, test, environment, dependency, evidence, and requirement failures | Non-reproduction or a single exit code cannot establish a software fix |
| Preserve contradictory evidence | Append-oriented evidence journal and hypothesis relationships | New observations do not overwrite failed tests or discard contradictions |
| Revise strategies from observations | New evidence can produce a new evidence-linked decision | Revision cites observations and remains reproducible from its inputs |

Their machine identifiers are `RECONSTRUCT_DECISIONS`, `CHALLENGE_ASSUMPTIONS`,
`DISTINGUISH_FAILURE_ORIGINS`, `PRESERVE_CONTRADICTIONS`, and
`REVISE_FROM_OBSERVATIONS` respectively.

The core exposes `FoxEngine.analyze` and `FoxEngine.reconstruct`; hypothesis
evaluation is `fox_engine.hypotheses.evaluate`. Concrete record shapes are defined
by the [schemas](../schemas/); the engine, hypothesis, evidence, and authority
modules implement the corresponding boundaries. Tests must challenge each
contract with both expected and contrary observations.

The vocabulary separates `OBSERVED_FACT`, `HYPOTHESIS`, `ASSUMPTION`, `PROPOSAL`,
`REJECTED_HYPOTHESIS`, `VERIFIED_CONCLUSION`, and `UNRESOLVED`. An observed fact
records what a stated source observed; it is not a guarantee that the source is
honest or that a causal interpretation is correct. A verified conclusion must
state the proposition and scope supported by evidence.

Unsupported claims must be withheld, but lack of support alone is not a logical
disproof. Rejected hypotheses remain available for historical reconstruction
and may be reconsidered when assumptions or evidence change.

Creativity grants no operational authority. A strategy may propose a novel
architecture without receiving permission to run commands, inspect credentials,
modify other projects, or publish content.
