# Rejected or limited hypotheses

| Claim | Status and evidence |
| --- | --- |
| A content hash makes local evidence immutable | REJECTED: a writer can recompute hashes or truncate a complete suffix; external anchors are required for rollback detection |
| A later successful run solves the original failure | REJECTED as a general rule: core regression tests preserve the original failed record and uncertainty |
| Every validator rejection calls for changing the validator | REJECTED as a general rule: six synthetic forbidden-inline-program fixtures fail while valid controls pass |
| Pretty JSON can be piped unchanged into a JSON-lines adapter | REJECTED: observed INVALID_REQUEST responses for individual physical lines; compact request fixture fixes framing |
| PowerShell Get-Content -Raw adds no extra request line | REJECTED for the tested pipeline: one valid response followed by rejection; line-oriented Get-Content fixes the request |
| FOX architecture templates prove fitness for a vision | UNSUPPORTED: they only meet the structural comparison contract |
| Generic JSON transport establishes Codex/Claude/Gemini/Qwen compatibility | UNSUPPORTED: each host integration still requires separate testing |

The CAE history is user-supplied and authorized, not independently verified by
these tests. Synthetic examples support the transferable tactic only.
