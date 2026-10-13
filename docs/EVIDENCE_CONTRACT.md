# Evidence contract

Evidence records describe observations and their provenance. They support record
and project identity, timestamp, observed condition, source, tool identity,
artifact hashes, test-command summary, exit status, hypothesis and decision
relationships, confidence qualification, environment, and reproduction steps.
The exact accepted shape is
[`evidence.schema.json`](../schemas/evidence.schema.json).

An evidence record must distinguish its observed condition from a causal claim.
An exit status is a tool result, not a universal verdict. A command summary is
documentation, not executable authority. Do not embed credentials, personal data,
hidden model reasoning, or private project content.

The journal is append-oriented: a later successful test creates a new record,
with new identity and context, while the failed record remains intact. Corrections
must be explicit new information rather than silent replacement. Hypothesis
relationships preserve both supportive and contradictory observations.

## Integrity and verification

Content hashes support consistency checks against available records and artifacts.
Independent verification must re-compute the applicable hashes and detect
malformed records, broken links, and unexpected changes rather than trusting the
writer's success response. Keep the reproduction context so that integrity checks
can be supplemented by a new experiment.

Local hashes do not establish cryptographic immutability, trusted timestamps,
authorship, or the truth of an observation. A person with full write access can
replace a journal and recompute its hashes. Detecting complete replacement or
truncation requires an independently retained checkpoint or external trust anchor.

Journal consistency, artifact-byte consistency, and reproduced experimental
results are different claims. State which one was verified. The concept foundation
does not promise durable transactional storage under every crash, hostile writer,
or concurrent append scenario; consult [LIMITATIONS.md](LIMITATIONS.md).

## Python journal API

`EvidenceJournal(path).append(record, permit=permit)` requires a current permit
for `Operation.WRITE_EVIDENCE`, the exact journal path, and resource
`"evidence-journal"`. Parent directories must already exist. The writer snapshots
the record, validates its contract, checks the prior chain, refuses duplicate
record identities, appends a new hash-linked envelope, and flushes the file.
An incomplete last line is an error to investigate; appending does not repair or
discard it. Advisory locking prevents cooperating simultaneous writers but is
not protection from an attacker who bypasses the protocol.

`fox_engine.evidence.verify_journal(path)` verifies envelopes, record structure,
identities, sequence, and content hashes. It reads the supplied local path and
does not create files, execute reproduction steps, or verify artifact contents.
The SDK caller must enforce read authority for that path. In contrast, the
standard-input/output `verify_evidence` operation only validates supplied records
and their distinct identities; it takes no filesystem path.
