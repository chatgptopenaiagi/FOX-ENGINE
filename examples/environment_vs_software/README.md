# Synthetic environment versus software comparison

With `PYTHONPATH=src`, run:

```text
python examples/environment_vs_software/run.py
```

An in-process stand-in receives a boolean capability flag. Its source identity,
fixture and dependency identity remain fixed. Capability absence returns the
synthetic status 78; capability presence returns 0. Both records remain in the
revised decision. No real platform, package, process or network service is probed.

The comparison challenges the scoped claim that both settings fail. Environment
attribution remains a hypothesis. Real investigation would require independent
reproduction while controlling source, fixture, dependency and environment
differences. One subsequent success is not proof that an intermittent defect
has been solved.
