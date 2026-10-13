# Agent compatibility

FOX has an agent-neutral core. It exchanges observable engineering decisions and
evidence summaries, not credentials or hidden model reasoning. Runtime analysis
requires no provider account or network access.

## Generic integration

The Python SDK exposes `FoxEngine().analyze(problem, evidence=None, hypotheses=None,
previous_decision=None)`. The standard-input/output adapter is launched with
`python -m fox_engine`; it accepts one JSON request per line.

```json
{"contract_version":"1.0","request_id":"registry-demo","operation":"strategies","payload":{}}
```

| Operation | Payload | Scope |
| --- | --- | --- |
| `analyze` | `problem`, optional `evidence`, `hypotheses`, `previous_decision` | Deterministic tactical decision |
| `strategies` | Empty object | Registered strategy definitions |
| `discover_architecture` | `vision`, optional `candidates` | Structurally complete competing proposals |
| `verify_evidence` | `records` array | Record structure and distinct identities only |

The standard-input/output `verify_evidence` operation accepts supplied records,
never an arbitrary filesystem path. It does not verify a journal's hash chain,
artifact bytes, or the authenticity of observations. Direct Python callers can
use `fox_engine.evidence.verify_journal(path)` for journal consistency checks.

Responses contain `contract_version`, `request_id`, `ok`, `result`, and `error`.
Invalid input produces `ok: false`, a null result, and an `INVALID_REQUEST` error
without echoing the rejected input. An unparseable or invalid envelope can have
a null request identity. Requests and responses are UTF-8 JSON lines; the adapter
accepts at most 1,048,576 bytes per request line, including its newline when present.
It emits one response per input line and exits with status 1 if any request fails.
See the schemas and
[integration examples](../examples/agent_integration/) for concrete records.

Hosts are responsible for launching the process, framing lines, handling errors,
retaining relevant decisions, and enforcing approval boundaries. No agent-specific
private API or undocumented hook is assumed. The adapter has no HTTP listener.

## Compatibility status

| Integration | Status | Evidence required before claiming compatibility |
| --- | --- | --- |
| Generic Python SDK | VERIFIED for bounded local tests on Windows with Python 3.14 | Direct calls with valid and invalid synthetic fixtures; see continuity test evidence |
| Generic JSON lines process | VERIFIED for bounded local tests on Windows with Python 3.14 | Local framing, error, and round-trip tests; see continuity test evidence |
| OpenAI Codex CLI | DESIGNED | An authorized, documented host round trip on a named version |
| Other OpenAI agents | DESIGNED | A separate integration test for each host |
| Claude coding agents | DESIGNED | A documented host round trip on a named version |
| Gemini agents | DESIGNED | A documented host round trip on a named version |
| Local Qwen agents | DESIGNED | A documented host round trip without private credential access |
| Future agents | DESIGNED | Contract conformance and host-specific boundary verification |
| Local MCP adapter | DESIGNED only | Protocol design, implementation, and conformance tests |

Generic JSON interchange does not establish compatibility with every listed
agent. No external agent integration is claimed verified by this foundation.

MCP is an extension candidate because it could expose bounded analysis tools
over a local transport. The initial decision is to keep it outside the core;
protocol versions, lifecycle, schema mapping, error behavior, and tool boundaries
must be investigated before implementation. Optional HTTP integration is also
deferred and must not expose a public endpoint by default.
