## Summary
Improve CFG construction: resolve **branch targets** (`bra` to labels) instead of only sequential edges.

## Why
Enables more accurate barrier/divergence analysis long-term.

## Scope
- Parse label lines / branch targets as they appear in PTX for the supported subset.
- Build successor edges for blocks ending in `bra`.

## Acceptance criteria
- [ ] Unit test with a tiny PTX snippet showing a branch creates a non-sequential edge.
- [ ] Document limitations in `docs/architecture.md`.
