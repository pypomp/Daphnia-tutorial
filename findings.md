# Findings: Advanced tutorial repair

## Requirements

- Propose a repair plan based on the advanced HTML/QMD, regular Python tutorial, R tutorial, validation scripts, render scripts, and READMEs.
- Explain sequencing and scientific reasoning.
- Modify the advanced QMD while leaving generated HTML and cluster wrappers unchanged in this turn.

## Research Findings

- The advanced `theta_Jn` base MCAP incorrectly uses level 0.8. The regular Python and R tutorials also use 0.8 for this profile. The project requirement is now 95% throughout all three sources; advanced sensitivity alternatives currently default to 0.95, so the existing advanced gate compares incompatible confidence levels.
- The advanced tutorial does not enable or assert JAX x64, although the regular tutorial documents catastrophic float32 cancellation in the negative-binomial likelihood.
- Cache metadata records backend and versions but not precision mode, permitting float32/x64 cache collisions.
- Core SIRJPF2 model chunks are identical between regular and advanced Python sources; the main discrepancy is numerical/search design.
- Advanced level 3 uses 10 starts and 100 iterations; the regular production tutorial uses 72 searches and 250 iterations.
- The advanced refinement retains random-walk SD 0.05 with slower cooling; all displayed refinement terminals degraded relative to their starts.
- PIF and MPIF best likelihoods satisfy the declared target tolerance, but the combined gate fails because within-method multi-start convergence fails.
- The strict render wrapper cannot publish an advanced render with known failed gates, despite the README describing that document as intentionally published for diagnostics.
- Existing CBS ResearchGrid commands use `grid_run --grid_gpu --grid_mem=62G --grid_submit=batch --grid_email="ybb@umich.edu"`.
- Current level wrappers select the advanced document through `DAPHNIA_DOC` in the submit environment; a positional document argument is safer on ResearchGrid.
- The modified advanced setup passes locally from the same `Python-code` working directory used by the cluster wrapper: JAX x64 is enabled, cache schema v5 is active, precision metadata is true, and the pinned Pypomp commit is detected.

## Issues Encountered

| Issue | Resolution |
|---|---|
| Setup test initially ran from the repository root and could not resolve the QMD path | Re-ran from `Python-code`, matching the render wrapper's working directory. |

## Technical Decisions

| Decision | Rationale |
|---|---|
| Use double precision for all scientific runs | Required for valid likelihood evaluation and fair R/Python comparison. |
| Test known parameter vectors before MIF | Identifies whether the model/likelihood or optimizer is responsible. |
| Pass `level=0.95` explicitly to all MCAP base and stability runs | The user requires 95% CIs exclusively, and stability comparisons require identical levels. |
| Split convergence from cross-method agreement | These are different claims and currently have different evidence. |
| Use positional wrapper arguments for document selection | Keeps the requested document in the ResearchGrid job command rather than depending on inherited environment state. |
| Remove advanced-QMD PASS/FAIL and figure suppression policy | Computations and diagnostics will remain visible; only genuine execution-invalidating conditions should stop the document. |

## 2026-08-23 Failed float64 level-2 render

- The requested advanced document ran on `researchgpu06` with the GPU backend and JAX x64 enabled.
- The wrapper recovered from Quarto/Deno exit 139 and produced a structurally valid standalone artifact.
- The artifact was not published because the QMD emitted five gate failures.
- The SRJF best MIF candidate matched the stored reference within MCSE, but a convergence failure triggered fallback to the R starting vector and caused a misleading reference-gate failure.
- The `theta_Sn` 95% MCAP interval was stable; the `theta_Jn` interval reached both grid boundaries and should be shown as computed without being presented as a validated finite interval.
- SIRJPF2 refinement degraded all three selected starts, and PIF/MPIF each had one converged start; these quantities should remain visible without suppressing their figures.

## Implemented transparent-reporting changes

- SRJF now always uses the best finite computed MIF candidate and reports per-start likelihoods, MCSEs, near-best count, and differences from the starting and stored-reference likelihoods.
- SRJF AIC is always calculated from the displayed likelihood estimates; the embedded-null difference, likelihood improvement, and combined MCSE are printed alongside it.
- MCAP now prints the raw profile table, base 95% interval, fit quantities, grid-edge distances, and sensitivity calculations, and always emits each figure.
- SIRJPF2 now prints reference differences, refinement results, near-best counts, and the PIF-minus-MPIF likelihood difference, and displays both figures unconditionally.
- `_emit_gated_figure` was replaced with an unconditional `_emit_figure` helper that preserves self-contained image embedding.
- Profile filtering of non-finite, implausibly high, and extreme low-likelihood points is computational preprocessing rather than reporting policy; it remains, and its output describes each exclusion directly.
- Candidate selection now raises `ValueError` when every value is non-finite instead of silently selecting index zero.

## Resources

- `Python-code/daphnia_tut_pypomp_advanced.qmd`
- `Python-code/daphnia_tut_pypomp.qmd`
- `R-code/daphnia_tut_R.qmd`
- `Python-code/validate_tutorial_html.py`
- `Python-code/render_gpu.sh`
- `Python-code/README.md`
- `/Users/ybb/Downloads/Research/Rpomp-Pypomp/PanelPomp-Python/run_commend.txt`

## 2026-08-24 author-comment revision

- The active advanced workflow is now GPU-only. It raises if JAX does not select the GPU backend, defaults to run level 2, defaults to float64, and does not silently fall back to CPU.
- `use_CPU=False` controls a separate CPU benchmark. Its heading, explanation, example code, computation, and timing output are all inside the conditional branch, so the current render performs no CPU benchmark and shows no CPU section.
- SRJF and SIRJPF2 run-level particle counts, repetitions, and MIF iterations now match their regular Python and R tutorial budgets. The displayed `RL` contains both model-specific level-2 budgets.
- Starting-point comparisons now use balanced good, medium, and poor groups with log-scale jitter standard deviations 0.08, 0.45, and 1.0. The first good start is the exact tutorial vector.
- Both model sections report initial and terminal likelihoods, MCSEs, improvements, group summaries, and start-quality traces under matched hyperparameters.
- The unit-specific SIRJPF2 comparison now begins PIF and MPIF from identical medium-quality starts and reports a 90%-of-median-gain iteration statistic alongside traces and final likelihoods.
- MCAP remains fixed at 95%. Raw profile and smoothing-sensitivity tables were removed, leaving one concise well-identified example and one concise weakly identified example.
- Static validation is the strongest safe local check because executing the QMD would violate the requested GPU-only constraint. All 40 Python chunks compile, the QMD has balanced fences and unique executable labels, and `git diff --check` passes.
- The standalone review checklist was visually inspected at desktop width. It contains ten completed implementation items, explicit pending cluster checks, two tables, and no horizontal overflow.
- A complete float32 versus float64 comparison cannot safely switch precision inside one Jupyter process. `render_gpu_precision_comparison.sh` therefore launches two independent complete level-2 renders, retains `_float32.html` and `_float64.html`, and leaves the standard `.html` as float64.
- The ordinary level-2 wrapper now explicitly sets `DAPHNIA_DOUBLE_PRECISION=1` and `DAPHNIA_USE_CPU=0`, so a later standard render cannot inherit the diagnostic float32 setting.
- The comparison wrapper continues to the float64 pass even if the diagnostic float32 pass fails. This protects the standard output while honestly recording that a complete float32 comparison was unavailable.

## 2026-09-02 comment export

- The completed level-2 float64 render was blocked by a stale release-validator
  sentinel, not by a numerical problem. `render_gpu.sh` packages, gates, and
  only then renames the standalone over the published file, so a failed gate
  leaves the new render orphaned and restores the old document. That is exactly
  the state the repository was in.
- The PIF/MPIF convergence-speed statistic printed NaN in that render because
  `_mif_trace_summary` summarised iteration 0, which records the starting
  parameters before any likelihood has been evaluated. The replacement,
  `mif_trace_curves`, drops iterations with no finite value.
- Four significant digits cannot be applied uniformly. A panel log likelihood of
  -498.954178 becomes -499.0, which cannot express the -0.17 difference from the
  stored reference that the document reports against a combined MCSE of 0.46.
  Log likelihoods therefore use two decimal places and everything else uses four
  significant digits; the split is dispatched per column name in `table_text`.
- A start-quality comparison in which every group converges shows only that the
  search is robust to the displacements tried. The `extreme` group exists to
  locate the failure boundary. Its jitter standard deviation of 2.5 is a
  judgement call and may land either side of the target, so the reporting was
  made robust to a group that produces no finite likelihood at all.
- Normalising a convergence-speed statistic by each group's own gain cannot
  compare groups. A group starting near the maximum has almost no gain to make,
  so it reaches 90% of it immediately or, when its median does not rise, never;
  a group with a large gain reaches most of it early while still finishing far
  below the others. The measure now times every group against one shared
  target: the best final median observed, less 10 log units.
- The extreme start displacement is bounded by the measurement model, not by
  taste. A fixed -150 penalty per violating observation floors the SRJF panel
  likelihood at -15,000, and a start displaced far enough to violate every
  bound sits on a flat surface with no gradient. That demonstrates the soft
  constraint rather than the optimiser, so the jitter is 1.8 rather than 2.5.
- Prose must not predict a result the render has not produced. The document
  cannot execute without the A100, so any sentence asserting that the extreme
  starts fail would be a prediction printed as a finding. The previous run's
  best of nine starts was a poor one, so displaced starts recovering is not
  unlikely here. `describe_arrivals` generates the sentence from the table.
- Comparing convergence speed across groups that begin hundreds of log units
  apart needs a logarithmic gap axis, not a zoomed linear one. On a linear
  zoom the group that starts nearest the maximum is flat against the top
  whatever window is chosen; on a log axis of the remaining distance to the
  best final median, a constant rate of approach is a straight line and the
  slopes are directly comparable.
