# Synthetic evidence-index investigation

Run from the repository root with `PYTHONPATH=src`:

```text
python examples/evidence_index_failure/run.py
```

The stand-in validator rejects any `inline_program` field and accepts a
nonempty list of command-description tokens. No token or inline marker is
executed. All thirteen fixtures are synthetic and remain in `fixtures.json`:
six rejected originals, six corrected entries and one valid control. Named
program files are inert descriptions, not files the example opens or runs.

The first decision records uncertainty. A paired comparison supplies new
observations while retaining the original six failed records byte-for-byte in
memory. The revised decision rejects a fixture-scoped defect explanation and
retains validator correctness as a hypothesis. The validator itself is unchanged.

This demonstrates `VALIDATOR_CORRECTNESS_BEFORE_VALIDATOR_MODIFICATION`.
It is inspired by the user-supplied case summary, not a reproduction of CAE.
Passing corrected fixtures does not prove that all validator behavior is correct,
nor does disappearance of a failure establish a general resolution.
