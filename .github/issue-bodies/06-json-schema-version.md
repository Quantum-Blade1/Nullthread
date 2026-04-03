## Summary
Add **JSON report versioning** for CI stability.

## Scope
- Add top-level field `schema_version` (string or int).
- Keep existing keys; only additive changes unless major bump.

## Acceptance criteria
- [ ] `tests/test_report_json_schema.py` asserts `schema_version` exists.
- [ ] Short note in README for integrators.
