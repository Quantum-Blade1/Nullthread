## Summary
Strengthen **barrier validation** using CFG-aware divergence reasoning (not only predicate-on-same-line heuristics).

## Scope
- Identify when a barrier post-dominates divergent control flow incorrectly.
- Use predicate/branch facts from CFG where possible.

## Acceptance criteria
- [ ] Fixture(s) that distinguish safe vs unsafe barrier placement.
- [ ] Update pass docs + expected false-positive notes.
