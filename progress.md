# Progress Log

## Session: 2026-08-19

### Phase: Diagnosis and repair planning

- **Status:** complete
- Reviewed the advanced source/render and compared them with the regular Python and R tutorials.
- Validated structural HTML packaging and identified four reported numerical failures.
- Isolated deterministic precision and MCAP-confidence-level defects.
- Distinguished model construction from optimization/convergence problems.
- Created a staged repair and verification plan; no tutorial source was modified.
- Revised the plan to require 95% MCAP intervals exclusively.
- Confirmed the existing CBS ResearchGrid GPU submission syntax from nearby project records and incorporated it into the plan.
- Modified `Python-code/daphnia_tut_pypomp_advanced.qmd` to enforce JAX x64, invalidate and fingerprint caches by precision, report ResearchGrid provenance, and use one 95% MCAP level for all base and sensitivity calculations.
- Confirmed all 37 advanced Python chunks compile with balanced fences and `git diff --check` passes.
- Executed the modified global setup locally at run level 1: x64 enabled, cache schema v5 active, precision metadata true, and the pinned Pypomp commit verified.

### Files created

- `task_plan.md`
- `findings.md`
- `progress.md`

## Test Results

| Test | Expected | Actual | Status |
|---|---|---|---|
| Advanced HTML structural validator | Self-contained and no empty figures | Passed | Pass |
| Advanced HTML numerical validator | Report known failed gates | Four failures reported | Expected failure |
| QMD syntax/fence compilation | Balanced Python chunks | 37 advanced and 30 regular chunks compile | Pass |
| SIRJPF2 core chunk comparison | Locate model transcription differences | Core chunks identical | Pass |
| Modified advanced setup chunk | x64 enabled and precision-aware cache metadata | Passed on CPU with pinned Pypomp commit | Pass |
| Full advanced-QMD run-level-1 smoke test | Execute every Python chunk | All 37 chunks completed in 398 seconds; theta_Jn reports a 95% CI | Pass |

## Error Log

- Critique (2026-08-19): QMD x64/cache/95%-MCAP changes are sound; weakest point is the proposed ResearchGrid command's invalid local macOS path. Confidence 72/100; make the level wrapper accept the document stem as a positional argument before cluster submission.

| Error | Attempt | Resolution |
|---|---:|---|
| Setup test could not find QMD when run from repository root | 1 | Re-ran from `Python-code`, matching the render wrapper; resolved |
| Planning-file update patch expected a missing section | 1 | Inspected files and applied a narrower matching patch; resolved |

## Session: 2026-08-23

### Phase: Transparent-reporting revision

- **Status:** complete
- Inspected the failed float64 level-2 standalone render and quantified every reported numerical failure.
- Replaced the advanced QMD's PASS/FAIL, fallback, suppression, and gated-figure policy with unconditional numerical and graphical reporting.
- Removed SRJF candidate fallback and AIC suppression; the best computed candidate is retained and all likelihood/AIC differences are printed.
- Replaced MCAP Boolean validation dictionaries and gated figures with unconditional MCAP summaries, numerical sensitivity tables, and figures.
- Replaced SIRJPF verdicts and figure suppression with reference differences, refinement tables, near-best counts, and an unconditional PIF/MPIF comparison.
- Changed the all-non-finite candidate fallback to a clear `ValueError`; configuration, version, x64, file, and unusable-input checks remain.
- Confirmed no gate/PASS/FAIL/suppression terminology remains in the advanced QMD, all 37 chunks compile, `git diff --check` passes, and the full CPU run-level-1 smoke test completes all chunks in 391 seconds.

## Session: 2026-08-24

### Phase: Detailed author-comment revision

- **Status:** implementation complete, level-2 A100 execution pending.
- Removed the Status section and the requested framework sentence.
- Made run level 2 the default and aligned SRJF and SIRJPF2 budgets with the R and regular Python tutorials.
- Required a GPU backend for the advanced workflow and placed the optional CPU benchmark wholly behind `use_CPU=False`.
- Added the `double_precision` switch, retained float64 as the default, and added a GPU float32/float64 negative-binomial comparison.
- Reduced displayed setup output to `run_level` and the model-specific `RL` dictionary.
- Added matched good, medium, and poor starting-point comparisons, group statistics, and traces to Sections 1 and 2.
- Added a common-medium-start PIF/MPIF convergence-speed comparison for the unit-specific SIRJPF2 model.
- Simplified MCAP to fixed 95% well-identified and weakly identified examples without raw focal-value or sensitivity tables.
- Created `Python-code/daphnia_tut_pypomp_advanced_review_checklist.html` and visually verified its desktop layout and document structure.
- Did not execute any Pypomp calculation locally, because the current request explicitly excludes CPU computation.
- Added `Python-code/render_gpu_precision_comparison.sh` for separate complete float32 and float64 level-2 GPU renders. The float32 result is diagnostic, the float64 result is copied for comparison, and the normal HTML remains float64.
- Added failure restoration so an interrupted float64 second pass cannot leave the float32 diagnostic as the standard tutorial output.
- Made the ordinary level-2 wrapper force float64 and keep the optional CPU benchmark disabled.

## Session: 2026-09-02

### Phase: Apply the 2026-09-02 comment export

- **Status:** implementation complete; GPU render pending.
- Established that the level-2 float64 render of the revised QMD had in fact
  completed and was left as `daphnia_tut_pypomp_advanced_standalone.html`. It
  was never published because `validate_tutorial_html.py` still required
  "not itself peer-reviewed", a string from the Status section the 2026-08-24
  review had deleted. Replaced that sentinel with "Complete tutorial
  precision:"; the existing render now passes the gate with exit 0.
- Comment 1: added a fourth start quality, `extreme`, at log-scale jitter 1.8,
  and moved run-level start counts from 3/9/18 to 4/12/20 so the four groups
  stay balanced. Groups that produce no finite likelihood are now named
  explicitly instead of vanishing from the figure.
- Comment 2: replaced the Diagnostic 1 bar panels with connected markers on a
  shared vertical axis, matching the regular Python and R tutorials.
- Comment 3: replaced per-chain MIF traces with one smoothed median curve and
  interquartile band per quality group in both sections, and added a printed
  convergence-speed table. Fixed the pre-existing NaN in the PIF/MPIF speed
  statistic: iteration 0 carries no evaluated likelihood, so summarising it
  made the first median NaN.
- Comment 4: added `sf`, `ll`, `interval` and `table_text`, and swept every
  numeric print and table. Log likelihoods keep two decimal places; this is a
  documented deviation from a literal four-significant-digit reading and is
  flagged for the author's decision.
- Verification: all 42 Python chunks compile, no duplicate labels, a
  cross-chunk symbol check resolves every name, 35 helper assertions pass, and
  `git diff --check` is clean. The document was not executed, because it
  requires a CUDA GPU.
- Recorded the whole revision in
  `Python-code/daphnia_tut_pypomp_advanced_update_20260902.html`.
- An adversarial review of the implementation produced four accepted findings,
  all applied: the single-panel trace figure was letting the extreme group
  flatten the three groups that converge, so it became two panels; the
  convergence-speed measure was normalised per group and therefore could not
  rank groups (and could return NaN for the fastest one), so it now uses one
  target shared across groups and across the two methods; the extreme jitter of
  2.5 would have put those starts on the flat -150 constraint floor where MIF
  has no gradient, so it was reduced to 1.8; and `difference_from_float64` was
  misclassified as a log likelihood and now takes four significant digits.
- A second round of review findings was applied: the zoomed second panel was
  replaced by the remaining gap to the best final median on a logarithmic axis,
  which is the only view that puts groups starting hundreds of log units apart
  on one comparable footing; prose that predicted the extreme group would not
  recover was replaced by `describe_arrivals`, which states the outcome from
  the computed table; `mif_trace_curves` copies after its boolean filter to
  keep a `SettingWithCopyWarning` out of three chunk outputs; the `-Inf`
  relocation offset is measured against the shared axis rather than one panel;
  the well-scaled baseline now excludes non-finite units as its label claims;
  and three dead assignments plus a `np.set_printoptions` call that implemented
  nothing were removed.
- Reversed the precision-comparison order on the author's instruction:
  `render_gpu_precision_comparison.sh` now renders float64 first and publishes
  it, then runs float32 as a diagnostic and restores the float64 document, so
  the standard output can never be the diagnostic. Exercised all four paths
  against a stubbed renderer: both passes succeeding, a failed float32, and a
  failed float64 with and without a previous document.
- The author confirmed the log-likelihood formatting exception, so log
  likelihoods stay at two decimal places and everything else keeps four
  significant digits.
