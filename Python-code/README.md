## PanelPOMP data analysis in Python: A four-species ecological system

The rendered tutorial is
[`daphnia_tut.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut.html).
The source is `daphnia_tut.qmd`.

> **Note.** The rendered document currently in this repository was produced
> before the present revision of `daphnia_tut.qmd` and does not correspond to
> it. A full run-level-3 render is pending; until it is committed, the source
> is the authoritative version.

### Prerequisites

This tutorial pins an exact Pypomp revision. It requires Pypomp 0.4.6.0 at commit
`ed95e3bd46c1cc188fc8f7d83e89c6d5035b977c`, and the released PyPI package is not
a substitute: the notebook reads the git HEAD of whatever `import pypomp`
resolves to and stops with an error if it is not that revision.

```bash
git clone https://github.com/pypomp/pypomp.git ~/git/pypomp
cd ~/git/pypomp
git checkout ed95e3bd46c1cc1
cd ~/git/Daphnia-tutorial/Python-code
pip install -e ~/git/pypomp
```

Installing Pypomp also installs JAX. The checkout location does not matter,
provided it is at the pinned revision and installed with `-e`. The rendered
document prints the resolved Pypomp path, commit and JAX backend at the top;
that banner is the record to quote when reporting a result.

### Running on a CPU or a GPU

Pypomp uses JAX and runs on either a CPU or an available accelerator. The
tutorial as published was produced on a single NVIDIA A40. CPU execution works
and is the default.

The backend is chosen by an environment variable that must be set **before**
JAX is first imported, because once JAX has initialised a backend,
`jax.config.update("jax_platform_name", ...)` is silently ignored:

```bash
DAPHNIA_USE_GPU=0 quarto render daphnia_tut.qmd   # CPU (default)
DAPHNIA_USE_GPU=1 quarto render daphnia_tut.qmd   # GPU
```

On a shared GPU, prevent JAX from reserving the whole card:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```

`render_gpu.sh` sets all of this and renders on a cluster GPU node. Quarto
exhausts memory while embedding resources on the cluster, so the wrapper renders
with external images and inlines them afterwards with `make_standalone_html.py`.
The JAX backend is part of the cache fingerprint, so CPU results are never
silently reused in a GPU render.

No CPU-versus-GPU speedup is quoted here, because a matched benchmark is not
part of the tutorial.

### Run levels

The compute budget is set by `DAPHNIA_RUN_LEVEL`, which controls particle
counts, iterations, independent starts and likelihood replicates together:

| Level | Purpose | Typical cost |
|-------|---------|--------------|
| 1 | Structural smoke test; numerical gates cannot pass | minutes |
| 2 | Numerical validation | about an hour on one A40 |
| 3 | High-compute candidate reproduction | several hours on one A40 |

```bash
DAPHNIA_RUN_LEVEL=2 DAPHNIA_FORCE_RECOMPUTE=1 quarto render daphnia_tut.qmd
```

A run is scientifically interpretable only when the numerical gates printed in
the document pass. Level 1 exists to check that the code executes; its gates
fail by construction and its figures are replaced by diagnostic callouts.

The R and Python tutorials use independent run-level definitions; the numbers
above do not correspond to the R levels.

Expensive results are cached under `cache_daphnia-qmd-cache-v*_<fingerprint>/`.
The fingerprint covers the notebook source, the data, the Pypomp commit, the
package versions, the backend and the run level, so edits to executable code can
never silently reuse stale numerical results. Set `DAPHNIA_FORCE_RECOMPUTE=1` to
ignore an otherwise compatible cache.

### Checking a change before a long run

`smoke_test.py` executes every code chunk at run level 1 on the CPU, in order,
without Quarto. It takes a few minutes and catches errors that would otherwise
appear an hour into a GPU job:

```bash
python smoke_test.py
```

It confirms that the code runs; it says nothing about whether the numbers are
right, since every gate fails at run level 1.

### Tutorial contents

1. **PanelPOMP model setup**: specifying a mechanistic model with shared and unit-specific parameters
2. **Panel iterated filtering**: implementing PIF and MPIF for likelihood maximisation
3. **Parameter estimation**: multi-stage optimisation with tempering
4. **Profile likelihood**: confidence intervals via the MCAP algorithm
5. **Model diagnostics**: unit-level likelihood decomposition and convergence checks
