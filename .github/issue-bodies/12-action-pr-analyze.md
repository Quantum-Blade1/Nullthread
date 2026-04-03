## Summary
Add a **GitHub Action** workflow that runs `nullthread analyze` on committed `.ptx` fixtures (or on artifacts produced in CI).

## Scope
- Workflow on `pull_request` + `push` to `main`.
- Upload JSON/HTML report as artifact (optional).
- Fail on new `CRITICAL` findings (optional toggle).

## Acceptance criteria
- [ ] Workflow file under `.github/workflows/` with clear comments.
- [ ] Document how to enable/disable strict failure in `CONTRIBUTING.md`.
