# Architecture

FOX separates engineering recommendations, evidence preservation, and operational
authority. Its concept core is a deterministic Python library. It neither calls
a model nor runs commands proposed by a strategy.

```text
Host agent or human
    |
    +-- Python SDK / versioned JSON lines adapter
            |
            +-- strict contract validation
            +-- tactical engine and strategy registry
            +-- hypothesis evaluation and discriminating tests
            +-- revisable architecture candidates
            +-- append-oriented evidence journal and verifier
            +-- scoped authority checker
    |
Host-owned approvals, filesystem access, tools, and execution
```

## Components and boundaries

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Contracts and schemas | Define accepted records and reject malformed input | Structural validity does not establish truth |
| Tactical engine | Select applicable tactics and record evidence-linked decisions | Rules do not infer arbitrary real-world causality |
| Strategy registry | Register independently described tactics | Registration does not launch code or additional models |
| Hypotheses | Compare claims with explicit supporting/contradicting observations | Contradictions and rejected claims remain visible |
| Architecture discovery | Offer alternatives with tradeoffs and acceptance criteria | Templates are proposals requiring domain review |
| Evidence | Preserve observations and check journal consistency | Local hashes are not immutable or authenticated storage |
| Authority | Evaluate exact requested operations within grants | Hosts must enforce the result at execution time |
| Adapters | Translate transport data to the same core contract | Transport compatibility is not agent compatibility |

The five governing principles map to interfaces and records in
[PHILOSOPHY.md](docs/PHILOSOPHY.md). Classification uses explicit problem context
and available evidence. It does not silently assign a probability to a model's
confidence or turn an unsupported explanation into an established fact.

## State and reproducibility

Requests carry stable identities and a contract version. Decisions retain their
input evidence references and any predecessor relationship. Revisions produce
new decisions; they do not rewrite their predecessors. Evidence failures and
later successes are separate observations.

Deterministic output requires the same validated inputs, strategy definitions,
and engine version. Time and environment belong in supplied observations;
the analysis algorithm must not depend on an ambient model or network state.
The evidence journal preserves records separately from policy decisions about
their interpretation.

## Extension policy

New animal strategies use the strategy contract and registry. Optional model
integration, agent-specific connectors, and an MCP adapter are future modules,
not prerequisites for offline use. No HTTP listener is part of this concept
foundation. Any future executor must enforce scoped grants, re-check filesystem
boundaries at use time, and retain the host's approval controls.

The initial repository is deliberately narrower than the full mission. See
[ROADMAP.md](ROADMAP.md) and [LIMITATIONS.md](docs/LIMITATIONS.md).
