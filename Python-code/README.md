## PanelPOMP data analysis in Python: A four-species ecological system

This directory holds two Python tutorials built on
[`pypomp`](https://github.com/pypomp). They analyse the same data with the same
models; they differ in how closely they follow the R version.

| Source | Rendered | What it is |
|---|---|---|
| `daphnia_tut_v2.qmd` | [`daphnia_tut_v2.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_v2.html) | A direct port of [`R-code/tut.qmd`](https://pypomp.github.io/Daphnia-tutorial/R-code/tut.html): the same sections, the same starting values, the same algorithmic settings, the same analyses and figures. |
| `daphnia_tut.qmd` | [`daphnia_tut.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut.html) | An extended version that adds numerical validation gates, profile screening, a CPU/GPU section and per-section timings. |

> **Status.** `daphnia_tut_v2.html` is a complete run-level-3 render and passes
> the release validator. `daphnia_tut.html` predates the current revision of its
> own source and should be regarded as out of date; read `daphnia_tut.qmd`
> rather than its rendered output until it is re-rendered.

### Prerequisites

The tutorials pin an exact Pypomp revision. They require Pypomp 0.4.6.0 at commit
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

### Double precision

`pomp` and `panelPomp` compute in double precision, and JAX defaults to single.
In single precision the particle filter can return log-likelihoods that are not
merely imprecise but impossible — positive values for a discrete likelihood —
and because a profile keeps the best of many searches at each grid point, it
preferentially selects them. One such artefact stretched a profile figure's
axis to +4000 and pushed its confidence interval onto the grid boundary.

`daphnia_tut_v2.qmd` therefore sets `JAX_ENABLE_X64=1` before importing JAX and
refuses to run without it. Double precision costs roughly four times the wall
time on a GPU, which is the single largest reason the run levels below are
slower than they look.

### Running on a CPU or a GPU

Pypomp uses JAX and runs on either. The backend is chosen by an environment
variable that must be set **before** JAX is first imported, because once JAX has
initialised a backend, `jax.config.update("jax_platform_name", ...)` is silently
ignored:

```bash
DAPHNIA_USE_GPU=0 quarto render daphnia_tut_v2.qmd   # CPU (default)
DAPHNIA_USE_GPU=1 quarto render daphnia_tut_v2.qmd   # GPU
```

On a shared GPU, stop JAX reserving the whole card:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```

`render_gpu_v2.sh` sets all of this and renders on a cluster GPU node. Quarto
exhausts memory while embedding resources there, so the wrapper renders with
external images and inlines them afterwards with `make_standalone_html.py`.

Two known quirks of the cluster toolchain. Quarto's Deno process segfaults
during HTML assembly *after* the document has been written, so the wrapper
packages the output regardless of the render exit status; an `exit=139` with a
successful `PACKAGE` line is a complete render. And two renders of the same
document in the same directory overwrite each other's intermediates, so submit
one job at a time.

### Run levels

`DAPHNIA_RUN_LEVEL` selects the compute budget. `daphnia_tut_v2.qmd` uses R's
`algorithmic.params` verbatim, so its levels are R's levels and its default is
2, the level at which the R document is published.

| Level | MIF particles / iterations | Purpose | Measured wall time |
|-------|---------------------------|---------|--------------------|
| 1 | 50 / 2 | Structural smoke test | about 7 minutes on a CPU |
| 2 | 500 / 320 | The level R publishes | not yet measured |
| 3 | 1000 / 250 | Production | 2 h 07 on an idle A40 |

`DAPHNIA_N_WORKERS` stands in for R's `getDoParWorkers()`. R registers ten
independent searches per worker in Section 1 and two per worker in Section 2, so
this setting scales the whole job; it defaults to 36.

```bash
DAPHNIA_RUN_LEVEL=3 DAPHNIA_N_WORKERS=36 ./render_gpu_v2.sh
```

`daphnia_tut.qmd` has its own run-level table, unrelated to R's, and renders in
about 9 minutes at level 2 and 24 at level 3 — but those figures are from
single-precision runs and are not comparable.

### Checking a change before a long run

`smoke_test.py` executes every code chunk at run level 1 on the CPU, in order,
without Quarto. It takes a few minutes and catches errors that would otherwise
appear an hour into a GPU job:

```bash
python smoke_test.py
```

It confirms that the code runs; it says nothing about whether the numbers are
right. When testing a change to the search code, raise `DAPHNIA_N_WORKERS`
enough to cross the 50-start batching boundary — a single batch hides an entire
class of indexing bug.

### Checking a rendered document

```bash
python make_standalone_html.py daphnia_tut_v2.html daphnia_tut_v2_standalone.html
python validate_tutorial_html.py daphnia_tut_v2_standalone.html --standalone
```

The validator checks that every numbered figure contains an image, that no local
resources remain after packaging, and that no numerical gate printed `FAIL`.
Note that the last check is vacuous for `daphnia_tut_v2.qmd`, which has no gates
because the R tutorial has none.

### Tutorial contents

1. **PanelPOMP model setup**: specifying a mechanistic model with shared and unit-specific parameters
2. **Panel iterated filtering**: PIF and, for a model with unit-specific parameters, MPIF
3. **Diagnostic 1**: parameter scaling verification
4. **Diagnostic 2**: evidence for unit-specific parameterization, compared by AIC
5. **Diagnostic 3**: MIF convergence traces
6. **Diagnostic 4**: confidence intervals via the MCAP algorithm
