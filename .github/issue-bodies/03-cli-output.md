## Summary
Improve **human-readable CLI report** formatting: readability, grouping, and stable ordering.

## Scope
- Group findings by kernel (optional) or sort deterministically.
- Reduce duplicated blank lines; keep evidence readable.
- Ensure severity tags stay consistent (`[CRITICAL]`, `[WARNING]`, `[INFO]`).

## Acceptance criteria
- [ ] Output changes are covered by a small pytest/snapshot or string assertions.
- [ ] No change to JSON schema (unless paired with schema version issue).
