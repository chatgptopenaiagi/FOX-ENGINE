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
