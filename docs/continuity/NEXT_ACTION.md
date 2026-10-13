# Next executable action

After the initial public checkpoint, inspect GitHub's `concept-validation`
workflow for this exact commit. Verify all four Windows/Linux, Python 3.11/3.14
jobs, preserve any failure and correct its cause within FOX. Record the run URL
and commit identity only after GitHub confirms them.

For the next engineering increment, add optional externally retained anchors to
`verify_journal`: expected final hash and record count, strict input validation,
suffix-truncation and recomputed-replacement regression fixtures. Keep existing
unanchored integrity checking explicit. No automatic deletion or repair.

Resume by reading AGENTS, SESSION_CHECKPOINT, TEST_EVIDENCE and unfinished ideas;
inspect `git status --short --branch`, remote URL and `git log -3 --oneline`.
Do not restart completed foundation work. Use `.venv/Scripts/python` locally
with `PYTHONPATH=src` and `python -m unittest discover -s tests -v`.
