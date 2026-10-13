# Architecture discovery without an implementation

With `PYTHONPATH=src`, run:

```text
python examples/architecture_discovery/run.py
```

A synthetic sensor-interface vision receives two deterministic starting
templates: a modular process and a coordinator with a bounded worker. Each
contains component responsibilities, boundaries, interfaces, dependencies,
failure models, tests, deployment, recovery and acceptance criteria.

The comparison covers all eight required dimensions. These are revisable
proposals with unmeasured tradeoffs. The engine preserves the vision but does
not claim to understand it semantically or invent sensor protocols. A host agent
can submit its own candidates through `discover_architectures(vision, candidates)`.
No hardware access, model calls or implementation generation occurs here.
