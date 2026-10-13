# FOX engineering instructions

Scope all work to this repository. Do not read or modify sibling projects,
interrupt unrelated processes, inspect agent credentials, or change installed
AI tools. The user's FOX authorization permits reviewed commits and ordinary
pushes only to `chatgptopenaiagi/FOX-ENGINE`; never force-push.

Read `docs/continuity/SESSION_CHECKPOINT.json` and `NEXT_ACTION.md` when present.
Inspect Git status before edits. Preserve user files and contradictory evidence.
Use synthetic fixtures and observable evidence, never hidden reasoning traces.

Keep these five principles executable: reconstruct decisions, challenge
assumptions, distinguish environment from software, preserve contradictions,
and revise strategies from observations. Recommendations never grant execution
authority. Offline deterministic behavior is the baseline.

Run `python -m unittest discover -s tests -v` with `PYTHONPATH=src` before a
checkpoint. Run schema parity validation when the development dependencies are
available. Record actual failures and later corrections separately. Review the
entire staged tree for secrets, personal data, and provenance before publication.
Use status labels DESIGNED, IMPLEMENTED, TESTED, VERIFIED, BLOCKED precisely;
VERIFIED always states the scope of verification, never production readiness.

No reliable account-usage telemetry is assumed. Preserve checkpoints at completed
tasks and session boundaries. Never confuse context capacity with account usage.
