# Security

FOX's concept foundation is intended for local, bounded engineering analysis.
It is not an OS sandbox or a privileged execution service. Treat every request,
evidence record, strategy definition, and artifact path as untrusted input.

The default is `READ_ONLY_ANALYSIS`. Recommendations do not authorize commands.
Hosts must separately enforce their own permissions and execution boundaries;
a positive FOX policy result does not bypass a host denial. No HTTP server or
public network endpoint is enabled by this foundation.

The threat model includes malformed JSON, forged or contradictory evidence,
path traversal, symbolic-link escapes, excessive input, and misleading claims
of verification. It excludes a malicious administrator who can rewrite the
entire local evidence journal and its hashes. Hashes establish consistency
relative to available bytes, not authorship or trusted observation.

See [AUTHORITY_SHIELD.md](docs/AUTHORITY_SHIELD.md) for the scope of checks and
[LIMITATIONS.md](docs/LIMITATIONS.md) for remaining assurance gaps. Do not place
credentials, personal information, private agent traces, or unauthorized project
content in public examples or evidence records.

For a suspected vulnerability, use GitHub's private vulnerability reporting
feature if it is enabled for this repository. If no private channel is available,
open an issue requesting a private contact without including sensitive details
or an exploitable payload. Do not assume a response time or support commitment.

Version `0.1.0-concept` is experimental. A passing test suite verifies only its
documented cases; it does not certify suitability for hostile multi-user use.
