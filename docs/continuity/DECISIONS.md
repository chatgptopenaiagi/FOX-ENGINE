# Observable engineering decisions

1. Use a standard-library runtime and strict exported JSON contracts. Rationale:
   deterministic offline operation without provider or installation coupling.
   The internal validator supports only FOX's schema vocabulary; independently
   check it against jsonschema during development.
2. Strategies are data records explicitly registered by the host. There is no
   executable plugin discovery, animal-specific model process, or implicit tool
   execution. Creative reasoning remains the host model's responsibility.
3. Preserve an entire problem snapshot, evidence content hashes, hypothesis
   meanings, and parent decision identity in revisions. Earlier failure records
   cannot be removed or rewritten through the revision API.
4. Support alone remains HYPOTHESIS. Conflicting supplied relationships remain
   UNRESOLVED. Neither a passing run nor a hash proves causal resolution.
5. Supply generic competing architecture templates and accept host alternatives.
   Structural completeness does not establish suitability for the human vision.
6. Make grants exact in operation, path, resource and time. Deny links, traversal,
   ambiguous Windows paths and privileged operations. The checker is not an OS
   sandbox and does not authenticate its host. Journal writes recheck a permit.
7. Expose bounded JSON lines and a Python SDK. No network listener, MCP service,
   provider access, hidden reasoning collection, or claimed agent-specific
   compatibility belongs in the foundation.
8. Publish only authored FOX material and synthetic examples. Use the supplied
   CAE narrative as an attributed, independently unverified case study.
9. Preserve failures found during development alongside later passing checks.
   Failure disappearance by itself is not proof of repair; retain regression
   tests and identify the changed cause.
