## Summary
Support `--passes all` as an alias for running every registered pass.

## Scope
- Extend CLI parsing in `src/nullthread/cli.py`.
- Keep backwards compatibility with comma-separated pass names.

## Acceptance criteria
- [ ] `nullthread analyze ... --passes all` runs the full pass set.
- [ ] Invalid pass names still produce a helpful error listing valid options.
