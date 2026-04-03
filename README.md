# nullthread

**Static analysis for GPU kernels — catch correctness bugs and performance issues before you ever touch a GPU**

---

```
nullthread analyze matmul.ptx

[CRITICAL] Race Condition at matmul_kernel:42
  Thread group writing to smem[threadIdx.x] with no barrier
  before read at line 51 — consequence: non-deterministic output
  Fix: insert __syncthreads() after the tile load at line 42

[WARNING] Uncoalesced Memory Access at matmul_kernel:31
  Column-major global access across warp — 32 transactions where 1 is sufficient
  Estimated bandwidth waste: 96%
  Fix: transpose access pattern or use shared memory staging
```

---

## What this is

GPU kernels fail in ways that are invisible at runtime. A race condition on shared memory doesn't crash your kernel — it silently returns wrong numbers. An uncoalesced memory access doesn't throw an error — it just wastes 96% of your bandwidth. Neither shows up until you're already burning GPU hours

Nullthread reads your compiled PTX file and tells you about both of those things before you run anything. No GPU hardware required. No profiler to attach. One command, under 15 seconds

It runs five analysis passes over your kernel's intermediate representation:

- **Race condition detection** — shared memory writes without sync barriers
- **Sync barrier validation** — `__syncthreads()` inside divergent control flow
- **Memory coalescing analysis** — uncoalesced global memory access patterns
- **Occupancy estimation** — register and shared memory pressure limiting active warps
- **Warp divergence flagging** — branch conditions that serialize parallel threads

Each finding comes with a plain-English explanation, a description of what actually happens at runtime if the bug triggers, and a concrete fix suggestion specific to your kernel

---

## Quickstart

```bash
pip install nullthread
```

Compile your CUDA kernel to PTX:

```bash
nvcc -ptx your_kernel.cu -o your_kernel.ptx
```

Run the analysis:

```bash
nullthread analyze your_kernel.ptx
```

That's it. No GPU, no profiler, no configuration needed to get started

---

## Installation

**Requirements:** Python 3.10+, no GPU needed

```bash
# from PyPI (once published)
pip install nullthread

# from source
git clone https://github.com/Quantum-Blade1/Nullthread.git
cd Nullthread
pip install -e ".[dev]"
pytest -q
```

### CLI reference (v2)

```bash
nullthread analyze kernel.ptx
nullthread analyze kernel.ptx --passes race,barrier,coalescing,occupancy,divergence
nullthread analyze kernel.ptx --format json
nullthread analyze kernel.ptx --format html --output report.html
nullthread analyze kernel.ptx --no-ai
nullthread version
```

See [docs/architecture.md](docs/architecture.md) for the analysis pipeline.

### AI diagnosis layer (optional)

By default nullthread uses built-in templates to explain findings. For richer, kernel-specific explanations you can point it at a language model:

```bash
# Anthropic Claude
export NULLTHREAD_API_KEY=your-anthropic-key
export NULLTHREAD_MODEL=claude-sonnet-4-20250514

# or use a local model via Ollama (no API key needed)
export NULLTHREAD_BACKEND=ollama
export NULLTHREAD_MODEL=llama3
```

---

## Usage

```bash
# analyze a single kernel
nullthread analyze kernel.ptx

# run specific passes only
nullthread analyze kernel.ptx --passes race,coalescing

# output as JSON (useful for CI/CD)
nullthread analyze kernel.ptx --format json

# output as HTML report
nullthread analyze kernel.ptx --format html --output report.html

# disable AI diagnosis (uses static templates, faster)
nullthread analyze kernel.ptx --no-ai
```

---

## How it works

1. You compile your CUDA kernel to PTX using the standard NVIDIA toolchain
2. Nullthread parses the PTX and builds a thread-annotated control flow graph — a graph where every node knows which thread is executing it and what the thread index arithmetic looks like
3. Five analysis passes run in parallel over that graph
4. Each finding goes to the AI layer (or static templates) to generate a plain-English explanation with a fix
5. The report prints to stdout (or HTML or JSON depending on your flags)

The key thing that makes this different from general-purpose static analyzers is that Nullthread's CFG models GPU thread semantics explicitly — warp structure, thread index arithmetic, shared memory bank layout. Most analyzers have no concept of `threadIdx`. Without that model, you can't reason about which threads conflict

---

## Current accuracy

| Pass | Kernels tested | Detection rate | False positive rate |
|------|---------------|----------------|---------------------|
| Race Condition Detector | 20 | 85% | 10% |
| Sync Barrier Validator | 15 | 93% | 7% |
| Memory Coalescing Analyzer | 20 | 95% | 0% |
| Occupancy Estimator | 12 | 100% | 0% |
| Warp Divergence Flagger | 10 | 80% | 20% |

The race detector's false positive rate is the main known weakness — it's inherent to conservative symbolic reasoning about thread index ranges. The roadmap includes optional user annotations to reduce this for teams who want to invest in it

---

## What's not supported yet

- Cooperative groups
- Warp-level primitives (`shfl_xor_sync`, `__reduce_add_sync`, etc.)
- Dynamic parallelism
- AMD ROCm / HIP kernels (planned — see roadmap)

When Nullthread encounters these it explicitly says so in the report rather than silently skipping them

---

## Roadmap

**Next (1 month)**
- Complete warp divergence pass
- HTML report with source-annotated kernel view
- VS Code extension for inline warnings

**3–6 months**
- AMD ROCm and HIP kernel support
- PyTorch custom op build pipeline integration
- Accuracy benchmarks against FlashAttention and Triton kernels
- Ollama integration for fully local inference

**Later**
- Fine-tuned local model — eliminates any API dependency
- GitHub Action for automatic kernel analysis on PRs
- CI/CD integration guide

---

## Contributing

Contributions are welcome — especially if you write GPU kernels professionally and have hit the kinds of bugs Nullthread is designed to catch. Your real-world test cases are more valuable than synthetic ones

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started

The areas where help is most needed right now:
- Extending the PTX parser to cover cooperative groups and warp-level primitives
- HIP/ROCm backend
- VS Code extension
- Real-world kernel test cases for the accuracy suite

---

## Research background

Nullthread builds on a line of academic work in GPU static analysis:

- [GPUVerify (CAV 2014)](https://doi.org/10.1007/978-3-319-08867-9_5) — foundational two-thread abstraction for GPU race checking
- [RaCUDA (PMAM 2024)](https://dl.acm.org/doi/10.1145/3637314) — quantitative performance modeling for CUDA kernels
- [HiRace (SC 2024)](https://sc24.supercomputing.org/) — high-accuracy data race detection on real kernel corpora
- [OOPSLA 2024 race analysis paper](https://dl.acm.org/doi/10.1145/3689734) — theoretical grounding for conservative static race analysis

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
