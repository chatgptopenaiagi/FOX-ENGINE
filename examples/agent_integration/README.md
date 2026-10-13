# Agent-neutral request and Python SDK

`request.json` is synthetic and uses FOX JSON contract version `1.0`.
The CLI expects JSON Lines: exactly one complete JSON request per input line.
The fixture is deliberately stored on one line; pretty-printed multiline JSON
is not a valid JSON Lines stream.
It contains observable task context, with no credentials or private reasoning.
With `PYTHONPATH=src`, a host can send it to the local CLI using standard input.
For PowerShell:

```powershell
Get-Content examples/agent_integration/request.json | python -m fox_engine
```

For a shell supporting input redirection:

```sh
python -m fox_engine < examples/agent_integration/request.json
```

Use `Get-Content` without `-Raw` for this JSON Lines fixture: PowerShell can add
an extra blank input line when a raw string already ends with a newline. The
CLI correctly rejects blank lines as invalid requests.

The SDK accepts the same problem and evidence records:

```python
import json
from pathlib import Path
from fox_engine import FoxEngine

request = json.loads(Path("examples/agent_integration/request.json").read_text())
decision = FoxEngine().analyze(**request["payload"])
print(json.dumps(decision, sort_keys=True))
```

CLI responses wrap results with request identity, contract version, success and
error fields. Host agents must preserve the `requires_authorization` flag for
test proposals. Receiving a recommendation does not authorize a subprocess.

This demonstrates the local JSON and SDK contract only. Codex, Claude, Gemini,
Qwen and other external agent integrations each require separate compatibility
verification; this example does not certify any of them. No HTTP listener or
model connection is started.
