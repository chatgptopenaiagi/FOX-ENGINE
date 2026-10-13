# Nondestructive authority shield

The default authority is `READ_ONLY_ANALYSIS`, represented in the Python shield
by `Operation.ANALYZE` and `Operation.READ_EVIDENCE`. FOX may inspect supplied evidence,
analyze supplied source context, and propose architectures, strategies, tests,
and decision records. A proposal never grants execution authority.

| Category | Default behavior |
| --- | --- |
| Analysis of supplied records | Allowed within validated input scope |
| Workspace file creation or modification | Requires a scoped grant |
| Test execution, processes, dependency installation | Requires a scoped grant and host enforcement |
| Credential extraction and destructive file operations | Denied by default |
| Unrelated repository or protected AI installation changes | Denied by default |
| System security or account administration | Denied by default |
| Privileged commands or public network exposure | Denied by default |
| GitHub changes or publication | Unavailable through the concept checker; host actions require explicit applicable authorization |

The Python interface is `AuthorityShield(workspace).authorize(operation, path,
resource=..., grant=...)`. A `Grant` identifies an exact operation, path, resource,
and lifetime using `not_before` and `expires_at`; its validity interval includes
the start and excludes the expiry. A returned `Permit` must be rechecked through
`require` immediately before the host operation. A grant is supplied by the host;
FOX cannot prove that its issuer obtained human approval.

Broad natural-language requests for creativity
must not be interpreted as operational permission. Invalid, expired, mismatched,
or incomplete grants fail closed.

Paths must be checked against the approved workspace, including traversal and
symbolic-link escapes. String prefix checks are insufficient: a sibling whose
name begins with the workspace name is still outside it. Existing path components
must be resolved and the result checked against the intended boundary.
The concept implementation conservatively rejects all descendant symlinks and
Windows reparse points, including links whose current target is inside the
workspace. Network shares, device names, alternate streams, and selected sensitive
paths are unavailable. Sensitive filename rules are a heuristic, not a guarantee
that arbitrary file contents contain no secret.

The concept checker is a policy evaluator, **not an operating-system sandbox**.
Checking a path and later opening it can race with filesystem changes. A future
executor must enforce the policy at the actual tool boundary and use appropriate
platform primitives or isolation for hostile filesystems. The current engine
does not automatically execute commands it recommends.

The host's permissions remain authoritative even when FOX permits an operation.
FOX must not silently escalate privileges or bypass the host's approval system.
MIT permits users to modify the software; these safety defaults are not added
license restrictions.
