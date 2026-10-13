# Foundation test evidence

These entries preserve observed failures and later checks separately. They are
engineering summaries, not fabricated CAE logs. Local environment: Windows,
CPython 3.14.7, isolated repository virtual environment, public PyPI development
tools pinned in requirements-dev.txt. No external model or Qwen service was used.

## Observed failures retained

1. An intermediate complete suite ran **55 tests, 2 failures**. The failing tests
   were `test_standalone_evaluation_cannot_erase_historical_evidence` and
   `test_test_actions_cannot_declare_authorization_unnecessary`. Both failures
   reported `AssertionError: ContractError not raised`. The first exposed missing
   historical-evidence retention in standalone evaluation; the second exposed
   an absent relationship between TEST_EXECUTION and its authorization flag.
   Correction: require prior evidence IDs and links; constrain action variants
   in both runtime and exported JSON contracts. The regression tests remain.
2. The independent review's default-Python run lacked optional jsonschema, so its
   parity test was skipped. This was a development-environment dependency gap,
   not a passing parity result. The repository virtual environment supplies the
   dependency; final parity checks below ran without skips.
3. The initial agent-integration fixture was pretty multiline JSON. Piping it
   into the JSON-lines adapter returned INVALID_REQUEST for physical lines,
   exit 1. Correction: store one complete request per line.
4. Piping that corrected file with PowerShell `Get-Content -Raw` produced an
   extra blank line, one success followed by INVALID_REQUEST, exit 1.
   Correction: use line-oriented `Get-Content` in the documented command.
   The adapter still rejects blank/malformed requests; the validator was not
   weakened to hide a fixture error.

## Subsequent successful checks

The first staged-content scan also flagged its own personal-home detection
pattern literal. Inspection confirmed a scanner-source false positive. Splitting
the literal at construction preserved the compiled detection rule and removed
the self-match; no file or finding category was exempted.

- `PYTHONPATH=src .venv/Scripts/python -m unittest discover -s tests -v`:
  **63 tests passed, 0 failures, 0 skips**, exit 0. Includes independent schema
  validation, historical reconstruction, contradictions, exact authority grants,
  Windows symlink/reparse escape rejection, journal tampering/torn writes,
  transport abuse recovery, and synthetic examples.
- `PYTHONPATH=src .venv/Scripts/python tools/export_schemas.py --check`:
  8 exported schemas match their runtime definitions, exit 0.
- Three example scripts: exit 0. Evidence-index example retained six failed
  observations plus seven corrected/control observations with unchanged validator
  source. Environment example returned simulated statuses [78, 0]. Architecture
  example returned two PROPOSAL structures with all eight comparison dimensions.
- Corrected PowerShell JSONL example: exit 0, `ok: true`, request identity
  `synthetic-agent-request`.
- Initial source/wheel build succeeded. Source-manifest review identified that
  schemas/examples needed explicit inclusion; MANIFEST.in was added. Final build
  and installed-wheel checks are recorded by the publication checkpoint.
- Development dependency consistency: `pip check` reported no broken requirements.
- Final `python -m build --no-isolation`: source archive and wheel built, exit 0.
  Source archive inspected (100 members): required schemas/examples/continuity
  included; pre-existing text document, local logs and virtual environment absent.
- Installed wheel imported using `python -I`, with source PYTHONPATH ignored:
  SDK and adapter smoke passed, eight strategies returned. No runtime dependency
  installation was needed (`pip install --no-deps`).

These tests verify bounded behavior, not production security, truth of supplied
observations, real CAE outcomes, real-agent integrations, or improved engineering
performance. Remote CI results are recorded only after GitHub confirms them.

## Initial remote CI: preserved portability defect

[Run 38368028648](https://github.com/chatgptopenaiagi/FOX-ENGINE/actions/runs/38368028648)
tested foundation commit `c3803f08d863f16bad70bfeaf5ff2e77d3b8f4a6`.
Windows/Python 3.14 and Ubuntu/Python 3.14 passed. Both Python 3.11 jobs failed
during import before schema checking or tests, with
`TypeError: 'function' object is not subscriptable` in StrategyRegistry.select's
return annotation. The earlier class method named `list` shadowed the built-in
under Python 3.11's eager annotation evaluation. This is a FOX portability defect
within its declared support range, not an unsupported environment.

Correction: postpone annotation evaluation in the strategies module. The original
failed run remains public. A later passing 3.11 run is required to verify this
correction; local Python 3.14 success alone is insufficient.

## Verified portability correction and anchor increment

[Run 38368299656](https://github.com/chatgptopenaiagi/FOX-ENGINE/actions/runs/38368299656)
at commit `1226385bc13ec8d6c5928fb235c373c0de1de771` passed all four jobs:
Windows and Ubuntu, each with Python 3.11 and 3.14. Each job reported 63 tests,
OK, without skips; schema, source/wheel build and installed SDK checks also passed.
This verifies the specific portability correction and bounded foundation suite.

The next increment added optional trusted journal count/hash snapshots. Targeted
evidence suite: 19 tests passed. Full local suite: **70 tests passed, 0 failures,
0 skips**, exit 0. Seven new tests cover exact and empty anchors, malformed pairs,
suffix and complete truncation, recomputed replacement, stale snapshots after
legitimate growth, and no file creation. Independent code review found no
substantive issues. Cross-platform results for this increment are recorded only
after its own CI run completes.

Publication checks before the foundation push inspected all 75 staged regular
files, scanned their exact contents, reviewed synthetic/provenance constraints,
and found no remaining secret/personal-data findings. GitHub confirmed PUBLIC
visibility and the exact foundation and portability commit identities; ordinary
pushes only, no release/tag publication. Later checkpoints repeat staged review.

## Anchor increment remote verification and preservation

[Run 38368670971](https://github.com/chatgptopenaiagi/FOX-ENGINE/actions/runs/38368670971)
at commit `10520affdec6c708470c7dc473a21bef961c6dca` passed all four jobs,
each with **70 tests, 0 failures, 0 skips**. Windows/Ubuntu and Python 3.11/3.14
schema checks, package builds, installs and SDK smoke checks succeeded.
GitHub's API and Git remote refs confirmed that exact public main commit.

The final continuity-only checkpoint records this verified implementation commit.
Its own enclosing Git commit is resolved with `git log -1 --
docs/continuity/SESSION_CHECKPOINT.json`; embedding a file's enclosing commit hash
inside itself would be circular. The final report separately identifies the
actual pushed HEAD. No unfinished source changes are intentionally left outside
Git; local raw validation logs and build products remain ignored.
