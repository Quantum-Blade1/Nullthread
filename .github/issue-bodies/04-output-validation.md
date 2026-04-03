## Summary
Make `--format json|html` ergonomics explicit (error messages and/or defaults).

## Scope
Choose one behavior and document it:
- **Option A**: require `--output` for `html` (and optionally `json`).
- **Option B**: default output filenames (`report.html`, `report.json`) when omitted.

## Acceptance criteria
- [ ] Clear error message or default behavior implemented.
- [ ] README + `nullthread analyze --help` text updated accordingly.
