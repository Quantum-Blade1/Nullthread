# Contributing to nullthread

Thanks for wanting to contribute. This doc covers everything you need to go from zero to opening a pull request

---

## Before you start

If you're planning something big — a new analysis pass, a backend rewrite, a major refactor — open an issue first and describe what you're thinking. It's easier to align before you've written the code than after

For small stuff (bug fixes, doc improvements, new test kernels) just go ahead and open a PR

---

## Setting up locally

```bash
git clone https://github.com/yourusername/nullthread.git
cd nullthread
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Run the tests to make sure everything works:

```bash
pytest
```

---

## Where to contribute

These are the areas that need the most work right now:

**High priority**
- PTX parser coverage — cooperative groups and warp-level primitives (`shfl_xor_sync`, `__reduce_add_sync`, etc.) are not yet supported
- Warp divergence pass — it works but it's the least precise of the five passes, false positive rate is higher than we'd like
- Real-world test kernels — if you have CUDA kernels from a production codebase (with bugs or without), adding them to `tests/kernels/` with annotations is extremely valuable

**Medium priority**
- AMD ROCm / HIP backend — the PTX parser is NVIDIA-specific; a HIP equivalent would make nullthread useful for the entire GPU ecosystem
- VS Code extension — inline warnings in the editor is the highest-impact UX improvement
- Ollama integration — for fully local inference without any API key

**Always welcome**
- Documentation improvements
- Better error messages
- Performance improvements to the analysis passes
- Additional test cases

---

## Project structure

```
nullthread/
├── src/nullthread/
│   ├── parser/       # PTX lexer and parser
│   ├── cfg/          # thread-annotated control flow graph
│   ├── passes/       # the five analysis passes
│   ├── ai/           # AI diagnosis layer (pluggable backends)
│   ├── report/       # CLI, HTML, JSON output
│   ├── analyze.py    # pipeline orchestration
│   └── cli.py        # Typer CLI
├── tests/
│   ├── kernels/      # annotated `.ptx` fixtures (see matmul.ptx)
│   └── test_*.py     # pytest suite
└── docs/             # architecture docs and guides
```

---

## Adding a test kernel

Test kernels live in `tests/kernels/` as **PTX** files (compile with `nvcc -ptx` from CUDA source, or hand-crafted minimal PTX for the analyzer). Example:

```
tests/kernels/your_kernel/
├── kernel.cu          # CUDA source (optional, for documentation)
├── kernel.ptx         # compiled PTX (what Nullthread analyzes)
└── expected.json      # expected findings from nullthread
```

The `expected.json` format:

```json
{
  "findings": [
    {
      "pass": "race_condition",
      "severity": "CRITICAL",
      "kernel": "your_kernel_name",
      "line": 42,
      "description": "brief description of the bug"
    }
  ]
}
```

To compile the PTX from CUDA source:

```bash
nvcc -ptx -arch=sm_80 kernel.cu -o kernel.ptx
```

If you don't have a GPU or CUDA toolkit locally, you can compile on Google Colab (free) and commit the PTX directly

---

## Opening a pull request

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Add or update tests if you're changing analysis behavior
4. Run `pytest` and make sure everything passes
5. Run `ruff check src/` and fix any lint issues
6. Open the PR with a clear description of what changed and why

PR titles should be short and specific: `fix race detector false positive on barrier-guarded writes` not `fixed some bugs`

---

## Reporting bugs

Use the bug report issue template. The most useful thing you can include is the PTX file that triggered the wrong behavior — either a false positive (nullthread flagged something that's actually safe) or a false negative (nullthread missed a real bug)

---

## Code style

- Python 3.10+
- `ruff` for linting (config in `pyproject.toml`)
- Type hints on all public functions
- Docstrings on all public classes and functions
- Prefer wrapping long lines (ruff `E501` is not enforced by default)

---

## License

By contributing you agree that your contributions will be licensed under the Apache 2.0 license
