## Summary
Reduce **false positives** in the race pass via lightweight **address overlap reasoning**.

## Scope
- Track simple address expressions for shared memory ops (e.g., same base register + thread-dependent offset).
- If disjointness can be proven for representative thread indices, suppress or downgrade findings with metadata explaining why.

## Acceptance criteria
- [ ] At least one new fixture demonstrating a prior false positive becomes a non-finding (or informational).
- [ ] Document conservative assumptions.
