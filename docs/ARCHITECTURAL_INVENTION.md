# Architectural invention

A project can begin with a human vision and no implementation. FOX's discovery
workflow offers competing candidate structures that make assumptions and
acceptance criteria inspectable. The concept implementation uses deterministic
templates; it does not claim open-ended invention or validate domain expertise.

Each candidate should describe system boundaries, component responsibilities,
interfaces, dependency relationships, security boundaries, failure behavior,
testing, deployment, recovery, and acceptance criteria. Candidates remain
proposals until evidence establishes specific claims about them.

Compare every candidate across these dimensions:

| Dimension | Investigation |
| --- | --- |
| Complexity | How many concepts, interfaces, and coordination paths are introduced? |
| Reliability | Which failures can be contained and recovered from? |
| Security | Where does trust change, and what authority is required? |
| Maintainability | Can components change without unrelated changes? |
| Portability | Which assumptions depend on a platform or dependency? |
| Testability | Can important claims be tested with bounded, observable checks? |
| Resource requirements | What CPU, memory, storage, network, and operational effort are assumed? |
| Expected failure behavior | What happens when dependencies, inputs, or services fail? |

These comparisons are qualitative until measurements exist. A numerical score
would require a declared rubric and evidence; it must not masquerade as calibrated
probability or an objective optimum.

The host may supply additional architectures and falsification criteria. Keep
alternatives that lose the first comparison, along with their rejection reasons.
If new constraints invalidate the current choice, those alternatives may become
useful again. Project-specific gates should follow risks and dependencies, not
a universal M0-M7 sequence.

See the synthetic [architecture discovery example](../examples/architecture_discovery/).
