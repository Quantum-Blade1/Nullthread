## Summary
Upgrade the coalescing pass toward a more **hardware-faithful model** (warp lanes, alignment, element size).

## Scope
- Start with global loads of common sizes (`f32`, `u32`) and simple address forms.
- Emit structured metadata: estimated transactions / striding classification.

## Acceptance criteria
- [ ] Tests with paired coalesced vs intentionally strided patterns.
- [ ] Clear limitations section in finding metadata or docs.
