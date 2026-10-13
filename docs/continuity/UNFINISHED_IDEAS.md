# Unfinished ideas

All items below are DESIGNED or exploratory, not verified capabilities.

- Follow-up to the now implemented optional journal count/hash comparison:
  design independently trusted anchor storage and authentication. Current tests
  cover suffix truncation and recomputed replacement against host-supplied anchors.
- Test simultaneous writers and abrupt interruption in controlled temporary
  workspaces. Do not silently repair torn journals; propose a new recovery artifact.
- Build an MCP adapter only after protocol/version selection and conformance
  tests. Keep it local and preserve the no-execution/no-credential boundary.
- Expand architecture candidate schemas and trace tradeoffs to evidence IDs;
  test host-supplied domain-specific alternatives against acceptance criteria.
- Verify each target agent using documented interfaces and synthetic missions.
  Do not access credentials or hidden traces. Compatibility cannot be inferred.
- Design comparative benchmarks with equivalent tasks, tools, budgets, and
  independent acceptance checks. Preserve unfavorable outcomes and uncertainty.
- Consider a host-enforced isolated execution adapter separately from planning.
  The current authority checker cannot eliminate TOCTOU or constrain malicious
  callers with unrestricted Python/OS access.
