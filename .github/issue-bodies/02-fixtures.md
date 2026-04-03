## Summary
Add small **PTX fixtures** under `tests/kernels/` so each pass has at least one deterministic test case.

## Scope
- Add 2–3 minimal `.ptx` files (or one file with multiple kernels) that trigger:
  - race (shared write → read without barrier)
  - barrier (predicated `bar.sync` or clearly divergent barrier pattern)
  - coalescing (thread-dependent/strided global load)
- Add pytest assertions on `ViolationKind` (no AI / `--no-ai`).

## Acceptance criteria
- [ ] New fixtures committed under `tests/kernels/`.
- [ ] Tests run in CI without GPU/CUDA.
