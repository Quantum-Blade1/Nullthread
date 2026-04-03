## Summary
Improve **`.loc` handling** and line attribution in findings.

## Scope
- Store file id + source line where available.
- Ensure findings prefer mapped source lines over raw PTX line numbers consistently.

## Acceptance criteria
- [ ] Fixture-based test proves expected line numbers for a controlled `.loc` sequence.
- [ ] Brief documentation update in `docs/architecture.md`.
