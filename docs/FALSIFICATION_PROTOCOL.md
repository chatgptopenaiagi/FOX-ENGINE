# Falsification protocol

Start with the failed observation and its reproduction context. Separate the
observation from the causal explanation. A nonzero exit status alone does not
identify the defective component.

| Competing explanation | Discriminating investigation |
| --- | --- |
| Implementation defect | Hold input and environment fixed; compare the failed behavior with the requirement |
| Invalid input | Validate the original bytes against the documented input contract |
| Correct validator rejection | Reproduce the rejection and inspect the exact rejected rule before proposing changes |
| Incorrect test construction | Inspect fixture assumptions and independently check the asserted expectation |
| Incompatible environment | Re-run a bounded case in a documented compatible environment |
| Dependency behavior differs | Record dependency versions and compare a minimal boundary case |
| Incomplete evidence | Obtain the missing command, output, status, or artifact before concluding |
| Inconsistent requirement | Construct a concrete case that cannot satisfy the stated requirements together |

A test proposal needs a bounded action, required authority, expected observations
under competing hypotheses, and a stop criterion. The host controls execution.
Do not change several variables at once and then claim to know the cause.

`VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION` is a first-class reusable
tactic: inspect what was rejected, reconstruct the applicable rule, and test
whether enforcement was correct before weakening a guard. A validator can be
wrong; the tactic requires evidence rather than assuming either answer.

Record supportive and contradictory observations separately. Absence of support
keeps a claim unresolved; an explicit contradiction may justify rejection within
the tested scope. If both support and contradiction exist, preserve both and
investigate their differing assumptions or contexts.

A failed run followed by a successful run is two observations. It does not prove
the defect was fixed, and the first run must not be rewritten. Preserve rejected
hypotheses and their evidence so future sessions can reconsider them honestly.
