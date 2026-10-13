# Limitations

`0.1.0-concept` is an experimental foundation. Its purpose is to make engineering
assumptions and evidence inspectable, not to certify a project or replace a host
agent's judgment.

- **Meaning is supplied.** Deterministic rules can validate records and compare
  explicit relationships; they cannot establish the truth of arbitrary prose or
  independently infer all causes of a failure.
- **Architecture candidates are proposals.** Templates help expose tradeoffs.
  They do not demonstrate original invention, suitability for an unfamiliar
  domain, or an optimal architecture.
- **Verification has scope.** Structural validity, journal consistency, a passing
  test, and real-world acceptance are different claims. None implies the others.
- **Local evidence is editable.** Hashes detect some inconsistencies but do not
  prevent a privileged writer from replacing records and recomputing hashes.
  Trusted timestamps, authenticated provenance, external anchors, and robust
  concurrent/crash recovery need further design and validation.
- **Authority checking is not isolation.** It does not stop a host from ignoring
  its result or eliminate filesystem races. No command executor or OS sandbox
  is supplied by the foundation.
- **Transport is not universal compatibility.** Each Codex, Claude, Gemini, Qwen,
  or other host needs its own documented integration test. MCP and optional model
  integration remain design work. No public HTTP endpoint is enabled.
- **External history is not authenticated.** CAE-inspired examples are synthetic
  and based on the authorized user-supplied account, not independent inspection.
- **Benefit is unmeasured.** No comparative benchmark yet establishes improved
  engineering outcomes, calibrated confidence, or a new software category.
- **Resource boundaries need continued review.** Local use with bounded inputs
  is the concept scope; hostile multi-user workloads need additional assessment.

Consult [the continuity checkpoint](continuity/SESSION_CHECKPOINT.json) for dated
implementation status, actual test results, failed experiments, and blockers.
Preserve these qualifications when presenting FOX to users or integrating it into
a host agent.
