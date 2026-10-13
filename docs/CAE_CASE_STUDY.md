# CAE case study and provenance

This case comes from an **authorized account supplied by the FOX project
initiator**. FOX has not independently verified the external CAE, ACPEX-7, or
M0-M7 events described here. No CAE source tree, private files, credentials,
uncommitted work, or runtime state was accessed to produce this foundation.
Examples in this repository are synthetic reconstructions.

The supplied account describes an `EVIDENCE_INDEX_INVALID_OR_DRIFTED` failure.
An investigation found six diagnostic runs containing inline programs disallowed
by the evidence indexer's rules. In that account, the validator was correctly
rejecting the records. The appropriate correction was to evidence handling while
preserving the validation rule.

The reusable tactic is
`VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION`:

1. Preserve the original failure and rejected input.
2. Identify the exact rule the validator enforced.
3. Compare the rejected input with that rule.
4. Test competing explanations using bounded synthetic cases.
5. Correct the demonstrated defect and retain both failure and correction evidence.

This tactic does not presume every validator is correct. It requires evidence
before changing a guard. The [synthetic example](../examples/evidence_index_failure/)
tests FOX's representation of the investigation; it does not authenticate the
external historical account.

Other supplied topics suggest transferable investigations:

| Topic | Generalized tactic |
| --- | --- |
| Intermittent broker failures | Retain each run's environment and avoid declaring resolution from non-reproduction |
| Audit availability | Distinguish missing evidence from evidence of successful execution |
| Cancellation races | Preserve event ordering and test competing cancellation outcomes |
| Deployment uncertainty | Separate local tests from deployment and acceptance observations |
| Unverified external acceptance | Leave external acceptance unresolved until directly observed |
| Regression preservation | Keep previously failing cases as future checks |
| Git checkpoints and long missions | Preserve decisions, contradictions, and an executable next step |

These are proposed engineering lessons, not claims that FOX has investigated
those systems. CAE's milestone sequence is not a universal architecture. FOX and
CAE remain independent projects.
