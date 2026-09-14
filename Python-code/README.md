## PanelPOMP data analysis in Python: A four-species ecological system

This directory holds two Python tutorials built on
[`pypomp`](https://github.com/pypomp). They analyse the same data with the same
models; they differ in how much machinery they add around the analysis.

| Source | Rendered | What it is |
|---|---|---|
| `daphnia_tut_pypomp.qmd` | [`daphnia_tut_pypomp.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp.html) | The tutorial proper: model construction, PIF and MPIF estimation, and the four diagnostics. Its results match the [R tutorial](https://pypomp.github.io/Daphnia-tutorial/R-code/daphnia_tut_R.html) up to Monte Carlo error. |
| `daphnia_tut_pypomp_advanced.qmd` | [`daphnia_tut_pypomp_advanced.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp_advanced.html) | The advanced version: GPU-only, double precision, run level 3. It adds a float32/float64 comparison, MIF searches from medium, poor and extreme starts, a PIF versus MPIF convergence-speed comparison, 95% MCAP intervals, per-section wall times, and an introduction to `bake` and `stew` computation archives with measured timings and reliability checks. |

> **Status: complete.** `daphnia_tut_pypomp_advanced.html` is the final
> run-level-3 float64 render, produced on a cluster GPU with Pypomp 1.0.2 at
> `2983c60`; `daphnia_tut_pypomp_advanced_float64.html` is an identical copy
> and `daphnia_tut_pypomp_advanced_float32.html` is the same document rendered
> in single precision, kept as a diagnostic. All three pass the release
> validator. `daphnia_tut_pypomp.html` is a run-level-2 render from
> 2026-08-21; its source was later updated for the Pypomp 1.0.0 API without
> changing the model or settings.

### Files

Required to reproduce either document:

| File | Why |
|---|---|
| `daphnia_tut_pypomp.qmd` or `daphnia_tut_pypomp_advanced.qmd` | the tutorial source |
| `bib-daphnia.bib` | bibliography named in the YAML header |
| `../data/Mesocosmdata.xls` | the data; sheets `dent-only treatments` and `both species combined` |

Plus Quarto, a Jupyter kernel, and the pinned Pypomp checkout below. Select the
interpreter with `QUARTO_PYTHON=$(command -v python)`; do not rely on a
`_quarto.yml`, which pins an absolute path valid only on one machine.

The render chain used for the published advanced document:

| File | Role |
|---|---|
| `render_gpu_precision_comparison.sh` | renders the advanced tutorial twice, float64 then float32, in separate processes |
| `render_gpu.sh` | renders one document on a cluster GPU node and packages it |
| `make_standalone_html.py` | inlines the figures after rendering |
| `embed_quarto_deps.py` | attaches the Quarto page dependencies and gates on them |
| `validate_tutorial_html.py` | release check on the packaged document |

### Prerequisites

The advanced tutorial requires Pypomp **1.0.2 at commit
`2983c603334611657ab575e5eff4932390880e55`**, which includes the bake/stew
feature. Install this exact development revision; the version number alone
does not identify a build containing these functions. Python 3.11 or newer
is required. The regular tutorial was written against 1.0.0 at
`232180acfafeefc7420755a9896827e3d3d0cf35`.

The advanced QMD checks both the imported checkout's Git commit and its
installed version metadata. For a new checkout, install into the Python
environment selected for Quarto:

```bash
git clone https://github.com/pypomp/pypomp.git ~/git/pypomp
cd ~/git/pypomp
git checkout 2983c603334611657ab575e5eff4932390880e55
python -m pip install -e .
python -m pip install jupyter-cache xlrd

git rev-parse HEAD
python -c "import pypomp; print(pypomp.__file__, pypomp.__version__)"
```

For an existing clone, fetch the feature branch with
`git fetch origin bake-stew-development` before checking out that commit.
An editable install can have stale version metadata after switching commits;
rerun `python -m pip install -e .` if the QMD reports a mismatch.

Set `QUARTO_PYTHON` to that environment's Python executable. The advanced
analysis requires a CUDA-capable JAX installation and a GPU and refuses to run
without one.

### Execution caching and computation archives

The advanced QMD enables `execute.cache: true`, which requires
`jupyter-cache`. Quarto can reuse notebook outputs when code is unchanged.
The SRJF examples additionally use `bake` for the initial likelihood array
and `stew` for named MIF outputs. When Python executes, these functions
validate declared dependencies and either compute and save or load results.
Their `.bake.pkl` and `.stew.pkl` files are separate from the remaining custom
cache files; the formats are not interchangeable.

After changing data, packages, or environment settings such as
`DAPHNIA_RUN_LEVEL` or `DAPHNIA_DOUBLE_PRECISION`, explicitly refresh Quarto's
cache so the QMD's provenance checks run:

```bash
quarto render daphnia_tut_pypomp_advanced.qmd --cache-refresh
```

To force the analysis computations to run as well:

```bash
DAPHNIA_FORCE_RECOMPUTE=1 quarto render daphnia_tut_pypomp_advanced.qmd --cache-refresh
```

For direct Quarto commands, the environment flag alone cannot bypass cached
execution. `render_gpu.sh` automatically adds `--cache-refresh` when
`DAPHNIA_FORCE_RECOMPUTE=1`, including calls from the precision wrapper. A
first render or a changed dependency still requires computation; the QMD's
conservative archive fingerprint also changes whenever the QMD file changes.
See [Quarto's caching documentation](https://quarto.org/docs/computations/caching.html).

### Double precision

`pomp` and `panelPomp` compute in double precision, and JAX defaults to single.
In single precision the particle filter can return log-likelihoods that are not
merely imprecise but impossible — positive values for a discrete likelihood —
and because a profile keeps the best of many searches at each grid point, it
preferentially selects them. One such artefact stretched a profile figure's
axis to +4000 and pushed its confidence interval onto the grid boundary.

Both tutorials therefore run in float64 by default. `daphnia_tut_pypomp.qmd`
sets `JAX_ENABLE_X64=1` before importing JAX and refuses to run without it;
the advanced tutorial exposes the switch as `DAPHNIA_DOUBLE_PRECISION` so the
float32 diagnostic can be rendered deliberately. Double precision costs
roughly four times the wall time on a GPU.

### Running on a CPU or a GPU

Pypomp uses JAX and runs on either. The backend is chosen by an environment
variable that must be set **before** JAX is first imported, because once JAX has
initialised a backend, `jax.config.update("jax_platform_name", ...)` is silently
ignored:

```bash
DAPHNIA_USE_GPU=0 quarto render daphnia_tut_pypomp.qmd   # CPU (default)
DAPHNIA_USE_GPU=1 quarto render daphnia_tut_pypomp.qmd   # GPU
```

The advanced tutorial is GPU-only; `DAPHNIA_USE_GPU=0` makes it stop with an
error. On a shared GPU, stop JAX reserving the whole card:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
```

`render_gpu.sh` sets all of this and renders on a cluster GPU node. The first
argument is the document stem and the second the run level:

```bash
./render_gpu.sh daphnia_tut_pypomp_advanced 3
```

Both may also be given as `DAPHNIA_DOC` and `DAPHNIA_RUN_LEVEL`; prefer the
arguments for batch submission, because a batch job does not reliably inherit
the submitting shell's environment. Quarto exhausts memory while embedding
resources on the cluster, so the wrapper renders with external images and
inlines them afterwards with `make_standalone_html.py`.

Three known quirks of the cluster toolchain. Quarto's Deno process segfaults
during HTML assembly *after* the document has been written, so the wrapper
packages the output regardless of the render exit status; an `exit=139` followed
by a `PUBLISHED` line is a complete render. That same segfault also skips the
stage that attaches Bootstrap and the other page dependencies, which leaves a
document that renders as unstyled pandoc output — `embed_quarto_deps.py`
reattaches them and then fails the job if they are still absent, so trust the
`PUBLISHED` line rather than the exit status. And two renders in the same
directory share `DENO_DIR`, `TMPDIR` and `.quarto/`, so run one at a time. If
Quarto segfaults with a stale Deno cache, clear it with `rm -rf /tmp/deno-$USER`
and rerun.

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

`daphnia_tut_pypomp_advanced.qmd` has its own run-level table, printed in its
setup chunk as `RL`, and defaults to level 2. The published document is level
3, and it prints the wall time of every expensive section at the end of each
model section.

### Rendering on CBS ResearchGrid

On the login node, update the tutorial checkout, activate the environment used
by the renderer, and install the exact Pypomp revision from the prerequisites
above. `render_gpu.sh` uses `/apps/anaconda3` and the `py313` environment:

```bash
cd ~/git/Daphnia-tutorial
git pull --ff-only
source /apps/anaconda3/etc/profile.d/conda.sh
conda activate py313

cd ~/git/pypomp
git fetch origin bake-stew-development
git checkout 2983c603334611657ab575e5eff4932390880e55
python -m pip install -e .
python -m pip install jupyter-cache xlrd
```

Use your existing cluster checkout paths if they differ from `~/git`. The
environment must already have working CUDA-enabled JAX. Submit from this
directory with the project's ResearchGrid GPU options:

```bash
cd ~/git/Daphnia-tutorial/Python-code
DAPHNIA_FORCE_RECOMPUTE=1 grid_run --grid_gpu --grid_mem=62G --grid_submit=batch \
  ./render_gpu.sh daphnia_tut_pypomp_advanced 3
```

Without `DAPHNIA_FORCE_RECOMPUTE=1` the renderer reuses matching cached
outputs. Monitor the job with `qstat -u "$USER"`; successful packaging ends
with `---PUBLISHED: daphnia_tut_pypomp_advanced.html`. Submit one render at a
time.

### Comparing float32 with float64

`render_gpu_precision_comparison.sh` renders the advanced tutorial twice. JAX
fixes its precision when it initialises, so a complete comparison needs two
processes rather than a switch inside one document. This is the command that
produced the published documents:

```bash
DAPHNIA_RUN_LEVEL=3 DAPHNIA_DOC=daphnia_tut_pypomp_advanced \
  ./render_gpu_precision_comparison.sh
```

float64 runs first and is the render that gets published; float32 follows as a
diagnostic and is never left in place as the standard document.

| File | Precision | What it is |
|---|---|---|
| `daphnia_tut_pypomp_advanced_float64.html` | float64 | the float64 render |
| `daphnia_tut_pypomp_advanced_float32.html` | float32 | diagnostic only; expect impossible positive log-likelihoods |
| `daphnia_tut_pypomp_advanced.html` | float64 | the published document, always a copy of the float64 render |

Both passes force recomputation, and `DAPHNIA_RUN_LEVEL` selects the budget
(default 2). If the float64 pass fails, nothing is published, the previous
document is restored, and float32 is not attempted. If only the float32 pass
fails, the float64 document stands and the script exits with the diagnostic's
status, so a non-zero exit accompanied by a `Float64 (published)` line means
just the diagnostic was lost.

### Running interactively on a chosen GPU

None of the scripts sets `CUDA_VISIBLE_DEVICES`, so whatever you export is
inherited all the way down to JAX. On a node you hold yourself, pick the free
device from `nvidia-smi` and run under `tmux` so the job survives a dropped
connection:

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv

conda activate py313
cd ~/git/Daphnia-tutorial/Python-code

tmux new -d -s daphnia \
  "CUDA_VISIBLE_DEVICES=0 DAPHNIA_RUN_LEVEL=3 DAPHNIA_DOC=daphnia_tut_pypomp_advanced \
   ./render_gpu_precision_comparison.sh > advanced_level3_precision.log 2>&1"
tmux attach -t daphnia          # detach again with ctrl-b d
tail -f advanced_level3_precision.log
```

One document, one precision, on one device:

```bash
CUDA_VISIBLE_DEVICES=0 DAPHNIA_FORCE_RECOMPUTE=1 ./render_gpu.sh daphnia_tut_pypomp_advanced 3
```

### Checking a rendered document

`render_gpu.sh` runs all of this. To repeat it by hand on a document that was
rendered with external resources:

```bash
DOC=daphnia_tut_pypomp_advanced
python make_standalone_html.py "$DOC.html" "${DOC}_standalone.html"
python embed_quarto_deps.py "${DOC}_standalone.html" --libs "${DOC}_files/libs"
python embed_quarto_deps.py --check "${DOC}_standalone.html"
python validate_tutorial_html.py "${DOC}_standalone.html" --standalone
```

The validator checks that every numbered figure contains an image, that no local
resources remain after packaging, and that the advanced document's precision
banner and section sentinels survived. Those sentinels belong to the advanced
document, so the structural check reports them missing on `daphnia_tut_pypomp.html`.
`embed_quarto_deps.py --check` is the separate guard against a half-assembled
page; it reads `${DOC}_files/libs`, which only exists immediately after a
render, so run it there rather than later.

### Tutorial contents

`daphnia_tut_pypomp`:

1. **PanelPOMP model setup**: specifying a mechanistic model with shared and unit-specific parameters
2. **Panel iterated filtering**: PIF and, for a model with unit-specific parameters, MPIF
3. **Diagnostic 1**: parameter scaling verification
4. **Diagnostic 2**: evidence for unit-specific parameterization, compared by AIC
5. **Diagnostic 3**: MIF convergence traces
6. **Diagnostic 4**: confidence intervals via the MCAP algorithm

`daphnia_tut_pypomp_advanced` adds, on top of the same two model sections:

- run levels and a GPU-only, double-precision workflow, with a float32 comparison
- `bake` and `stew` computation archives, with timing, correctness and invalidation checks
- MIF searches from medium, poor and extreme starting points, with convergence curves
- a PIF versus MPIF convergence-speed comparison from matched starts
- 95% Monte Carlo adjusted profile intervals for a well-identified and a weakly identified parameter
- per-section wall times
