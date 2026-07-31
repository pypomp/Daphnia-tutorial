## PanelPOMP data analysis in Python: A four-species ecological system

This directory holds two Python tutorials built on
[`pypomp`](https://github.com/pypomp). They analyse the same data with the same
models; they differ in how closely they follow the R version.

| Source | Rendered | What it is |
|---|---|---|
| `daphnia_tut_pypomp.qmd` | [`daphnia_tut_pypomp.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp.html) | A direct port of [`R-code/tut.qmd`](https://pypomp.github.io/Daphnia-tutorial/R-code/tut.html): the same sections, the same starting values, the same algorithmic settings, the same analyses and figures. |
| `daphnia_tut_pypomp_advanced.qmd` | — | An advanced version that does *not* replicate the R tutorial. It adds numerical validation gates, profile screening, a CPU/GPU section and per-section timings. |

> **Status.** `daphnia_tut_pypomp.html` is a complete run-level-3 render and
> passes the release validator. The advanced tutorial has no published document:
> its last render predates the current revision of its own source and was
> missing every MCAP figure, so it was withdrawn rather than corrected. Read
> `daphnia_tut_pypomp_advanced.qmd` until a fresh render lands.

### Files needed to reproduce `daphnia_tut_pypomp`

Required:

| File | Why |
|---|---|
| `Python-code/daphnia_tut_pypomp.qmd` | the tutorial source |
| `Python-code/bib-daphnia.bib` | bibliography named in the YAML header |
| `data/Mesocosmdata.xls` | the data; sheets `dent-only treatments` and `both species combined` |

Plus Quarto, a Jupyter kernel, and the pinned Pypomp checkout below. Select the
interpreter with `QUARTO_PYTHON=$(command -v python)`; do not rely on a
`_quarto.yml`, which pins an absolute path valid only on one machine.

Useful but not required: `render_gpu.sh` with its `render_gpu_level2.sh`,
`render_gpu_level3.sh` and `render_gpu_both.sh` wrappers (cluster submission),
`make_standalone_html.py`
(inlines images afterwards), `embed_quarto_deps.py` (attaches the Quarto page
dependencies, and gates on them), `smoke_test.py` (pre-flight check) and
`validate_tutorial_html.py` (release check).

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

`daphnia_tut_pypomp.qmd` therefore sets `JAX_ENABLE_X64=1` before importing JAX
and refuses to run without it. Double precision costs roughly four times the wall
time on a GPU, which is the single largest reason the run levels below are
slower than they look.

### Running on a CPU or a GPU

Pypomp uses JAX and runs on either. The backend is chosen by an environment
variable that must be set **before** JAX is first imported, because once JAX has
initialised a backend, `jax.config.update("jax_platform_name", ...)` is silently
ignored:

```bash
DAPHNIA_USE_GPU=0 quarto render daphnia_tut_pypomp.qmd   # CPU (default)
DAPHNIA_USE_GPU=1 quarto render daphnia_tut_pypomp.qmd   # GPU
```

On a shared GPU, stop JAX reserving the whole card:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```

`render_gpu.sh` sets all of this and renders on a cluster GPU node. It takes the
document stem from `DAPHNIA_DOC`, defaulting to `daphnia_tut_pypomp`. Quarto
exhausts memory while embedding resources there, so the wrapper renders with
external images and inlines them afterwards with `make_standalone_html.py`.

Three known quirks of the cluster toolchain. Quarto's Deno process segfaults
during HTML assembly *after* the document has been written, so the wrapper
packages the output regardless of the render exit status; an `exit=139` followed
by a `PUBLISHED` line is a complete render. That same segfault also skips the
stage that attaches Bootstrap and the other page dependencies, which leaves a
document that renders as unstyled pandoc output — `embed_quarto_deps.py`
reattaches them and then fails the job if they are still absent, so trust the
`PUBLISHED` line rather than the exit status. And two renders of the same
document in the same directory overwrite each other's intermediates, so submit
one job at a time.

### Run levels

`DAPHNIA_RUN_LEVEL` selects the compute budget. `daphnia_tut_pypomp.qmd` uses R's
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
DAPHNIA_RUN_LEVEL=3 DAPHNIA_N_WORKERS=36 ./render_gpu.sh
```

`daphnia_tut_pypomp_advanced.qmd` has its own run-level table, unrelated to R's.
It rendered in about 9 minutes at level 2 and 24 at level 3, but those figures
come from single-precision runs and are not comparable; treat its next level-2
run as the measurement. Render it by naming it:

```bash
DAPHNIA_DOC=daphnia_tut_pypomp_advanced ./render_gpu_level2.sh
```

### Rendering both tutorials

`render_gpu_both.sh` renders both, one after the other, in a single allocation:

```bash
DAPHNIA_RUN_LEVEL=2 ./render_gpu_both.sh
```

Do not submit the two documents as concurrent jobs. `DENO_DIR`, `TMPDIR` and
Quarto's `.quarto/` directory are per-user rather than per-job, and each level
wrapper clears the Deno cache as it starts, so a second job would pull that
cache out from under a render already in flight; two double-precision jobs also
contend for the card. Sequential rendering is what makes one submission safe.

Each document goes through the full chain, so anything that lands in place is
self-contained and correctly styled. The second is attempted even if the first
fails — the allocation is already paid for — and the closing summary lists each
document as published or not.

### Checking a change before a long run

`smoke_test.py` executes every code chunk at run level 1 on the CPU, in order,
without Quarto. It takes a few minutes and catches errors that would otherwise
appear an hour into a GPU job:

```bash
python smoke_test.py                             # daphnia_tut_pypomp.qmd
python smoke_test.py daphnia_tut_pypomp_advanced.qmd
```

It confirms that the code runs; it says nothing about whether the numbers are
right. When testing a change to the search code, raise `DAPHNIA_N_WORKERS`
enough to cross the 50-start batching boundary — a single batch hides an entire
class of indexing bug.

### Checking a rendered document

`render_gpu.sh` runs all of this. To repeat it by hand on a document that was
rendered with external resources:

```bash
DOC=daphnia_tut_pypomp
python make_standalone_html.py "$DOC.html" "${DOC}_standalone.html"
python embed_quarto_deps.py "${DOC}_standalone.html" --libs "${DOC}_files/libs"
python embed_quarto_deps.py --check "${DOC}_standalone.html"
python validate_tutorial_html.py "${DOC}_standalone.html" --standalone
```

The validator checks that every numbered figure contains an image, that no local
resources remain after packaging, and that no numerical gate printed `FAIL`.
Note that the last check is vacuous for `daphnia_tut_pypomp.qmd`, which has no
gates because the R tutorial has none. `embed_quarto_deps.py --check` is the
separate guard against a half-assembled page; it reads `${DOC}_files/libs`,
which only exists immediately after a render, so run it there rather than later.

### Tutorial contents

1. **PanelPOMP model setup**: specifying a mechanistic model with shared and unit-specific parameters
2. **Panel iterated filtering**: PIF and, for a model with unit-specific parameters, MPIF
3. **Diagnostic 1**: parameter scaling verification
4. **Diagnostic 2**: evidence for unit-specific parameterization, compared by AIC
5. **Diagnostic 3**: MIF convergence traces
6. **Diagnostic 4**: confidence intervals via the MCAP algorithm
