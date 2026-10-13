# Animal strategy taxonomy

Animals name reusable tactics, not autonomous personalities or separate language
model processes. The core selects applicable registered strategies and compares
their expected outputs and investigative cost.

| Strategy | Responsibility | Typical result |
| --- | --- | --- |
| OWL | Observe evidence and reconstruct history | A source-linked account of what is known and missing |
| FOX | Challenge hypotheses and implementation assumptions | Competing explanations and discriminating tests |
| WOLF | Analyze dependencies and coordination | A bounded task ordering with blockers |
| OCTOPUS | Explore alternative architectures | Several candidate structures with explicit tradeoffs |
| TORTOISE | Preserve continuity, provenance, and recovery | Durable evidence and an exact resumption task |
| EAGLE | Assess global architecture and consequences | Boundary, coupling, and failure-propagation review |
| ANT | Plan bounded verification and regression checks | Reproducible tests with acceptance and stop criteria |
| BEAVER | Plan maintainable construction | Implementation steps linked to interfaces and evidence |

Every strategy exposes `strategy_id`, `description`, `applicability_conditions`,
`required_inputs`, `expected_outputs`, `risk_level`, `authorization_requirements`,
`evidence_requirements`, `failure_conditions`, and `completion_criteria`.
The strategy schema defines their exact types and accepted values.

New strategy definitions are registered through the registry interface without
changing tactical engine code. Duplicate identities and malformed definitions
must fail validation. Registration only makes a tactic available; applicability
still depends on the engineering problem and supplied evidence.

Strategies must be testable independently. Tests should cover when a tactic
applies, when required information is missing, and when its completion claim
would be unsupported. Risk level and authorization requirements describe the
proposed investigation; neither grants permission to execute it.
