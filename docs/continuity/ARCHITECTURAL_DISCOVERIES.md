# Architectural discoveries

- A decision digest must bind the original requirements, not only recommended
  tactics. Otherwise two different problem descriptions can share one identity.
  The foundation stores the complete problem snapshot in the decision digest.
- Keeping raw evidence is insufficient if a revision removes the citation that
  ties it to a rejected hypothesis. Revision and reconstruction check both.
- Authorization requirements belong in machine contracts. A transport record
  must not label TEST_EXECUTION as requiring no authorization merely because its
  content digest is internally consistent.
- Boundary failures can originate in evidence preparation. The synthetic
  integration example repeated the validator lesson: pretty JSON and an extra
  blank line were incorrect JSON-lines input. Correct framing fixed the example;
  rejecting malformed input remained the intended behavior.
- Separate journal integrity, artifact-byte consistency and experimental truth.
  They require different verification and should never share an unqualified
  verified label.
- Cross-version failures can be source defects even when the newest runtime
  passes. The first remote matrix isolated eager annotation evaluation on
  supported Python 3.11; postponing evaluation fixed the declared support range.
- An exact journal anchor detects changed history relative to a trusted snapshot,
  but it also rejects valid growth. A mismatch is evidence of difference, not
  by itself evidence of an attack.
