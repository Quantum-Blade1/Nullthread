## Summary
Polish the README so new contributors can run Nullthread in under 2 minutes.

## Scope
- Document `nullthread analyze` with real flags: `--passes`, `--format`, `--output`, `--no-ai`, `version`.
- Add 3 copy-paste examples: CLI output, JSON to stdout, HTML to file.
- Link to `docs/architecture.md`.

## Acceptance criteria
- [ ] README includes the commands above and matches current CLI behavior.
- [ ] Mentions `pip install -e ".[dev]"` and `pytest` for contributors.

## Notes
Target repo layout: `src/nullthread/`, tests in `tests/`.
