# Task Plan: Apply 2026-08-24 advanced-tutorial review

## Goal
Apply every actionable review comment to the advanced QMD, make run level 2 the default GPU-only workflow, keep optional CPU material fully inactive and invisible when `use_CPU=False`, and produce a comprehensive HTML completion checklist.

## Current Phase
Phase 8 complete: the 2026-09-02 comment export is implemented and the release
validator no longer blocks publication. A float32/float64 level-2 GPU render is
pending.

## Phases

### Phase 1: Correct deterministic numerical defects
- [x] Enable and assert JAX double precision before importing JAX in the advanced QMD.
- [x] Include precision mode in advanced cache metadata and invalidate float32 caches.
- [x] Standardize advanced MCAP base and sensitivity calculations at 95% confidence.
- [ ] Standardize the regular Python and R tutorial sources at 95% confidence if they are included in the requested implementation scope.
- **Status:** in_progress

### Phase 2: Establish a fair reference baseline
- [ ] Re-evaluate the R/MLE reference vectors in Pypomp without optimization.
- [ ] Confirm data slices, state equations, parameter order, and likelihood aggregation.
- [ ] Define tolerances using repeated particle-filter MCSE rather than round numbers alone.
- **Status:** pending

### Phase 3: Repair optimization and convergence design
- [ ] Separate global search and local refinement budgets.
- [ ] Use at least the regular tutorial's search breadth/iterations for SIRJPF2.
- [ ] Reduce perturbation scale during refinement and retain non-degradation safeguards.
- [ ] Separate target-agreement and within-method convergence gates.
- **Status:** pending

### Phase 4: Re-run in escalating compute stages
- [x] Run CPU/run-level-1 structural smoke test.
- [ ] Run focused double-precision checks for MCAP and SIRJPF2 at level 2.
- [ ] Run level 3 only after level 2 passes or yields a diagnosed scientific non-identifiability result.
- [ ] Submit through CBS ResearchGrid using `grid_run --grid_gpu --grid_mem=62G --grid_submit=batch`.
- [ ] Pass document and run level as script arguments stored in the batch command, not as fragile submit-shell environment prefixes.
- **Status:** pending

### Phase 5: Align validation and publication policy
- [ ] Decide whether unresolved scientific diagnostics are publishable warnings or release failures.
- [ ] Make render scripts apply that policy explicitly per document.
- [ ] Correct README claims and add tests for precision, confidence level, and gate semantics.
- **Status:** pending

### Phase 6: Replace gates with transparent reporting
- [x] Inventory every gate, fallback, suppression branch, and gated figure.
- [x] Always retain and report the computed SRJF optimizer result; print reference differences and convergence counts without verdicts.
- [x] Always report SRJF AIC and MCAP results, sensitivity comparisons, and figures.
- [x] Replace PASS/FAIL prose with neutral numerical diagnostics.
- [x] Preserve runtime guards for genuine configuration, file, version, x64, and non-finite-input errors.
- [x] Compile every Python chunk and run the level-1 structural smoke test.
- **Status:** complete

### Phase 7: Apply detailed author comments
- [x] Remove the Status section and the specified framework sentence.
- [x] Make run level 2 the default and align the three budgets with the comparison tutorials.
- [x] Require a GPU for the active render and add an opt-in, fully hidden CPU comparison controlled by `use_CPU=False`.
- [x] Add a `double_precision` switch, default it to float64, and demonstrate float32 versus float64 on the active GPU.
- [x] Reduce setup output to a formal explanation of `run_level` and `RL`.
- [x] Replace mildly dispersed MIF starts with labeled good, medium, and poor starts under matched settings, with numerical and trace comparisons.
- [x] Add a matched medium-start PIF versus MPIF convergence-speed comparison for the unit-specific model.
- [x] Simplify MCAP to two 95% examples without raw focal-value or sensitivity tables.
- [x] Apply the same presentation and starting-point principles in Section 2.
- [x] Create and inspect a standalone HTML checklist that maps every review comment to the change and verification.
- [x] Add a two-process complete float32/float64 comparison and restore float64 for all standard later renders.
- **Status:** complete

## Decisions Made

| Decision | Rationale |
|---|---|
| Fix deterministic defects before spending GPU time | Current float32 and MCAP-level defects can invalidate expensive results. |
| Validate fixed reference vectors before optimization | This separates model/likelihood disagreement from search failure. |
| Treat weak identification separately from computation failure | A scientifically flat profile should not be disguised as an algorithm bug. |
| Use 95% confidence intervals exclusively | This is the user's inferential requirement and must be identical in base and sensitivity fits. |
| Make the document name a wrapper argument | ResearchGrid batch submission may not preserve environment prefixes reliably. |
| Modify only the advanced QMD in this implementation turn | The user requested modification of the singular attached QMD; generated HTML and cluster wrappers remain untouched. |
| Show computed results regardless of diagnostic quality | The user will assess numerical quality manually and does not want automated publication gates or AI-styled verdict language. |
| Default to run level 2 on GPU | This is the requested cluster run, and it prevents an accidental local CPU execution of an expensive tutorial. |
| Keep CPU comparison opt-in and non-rendering | The reviewer requested that the entire CPU block disappear when `use_CPU=False`; the current requested run must perform no CPU computation. |
| Use 95% MCAP only | The review explicitly rejects adjustable confidence levels and raw focal-value/sensitivity output. |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| Setup test could not find the QMD from repository root | 1 | Re-ran from `Python-code`, matching the Quarto and ResearchGrid wrapper working directory; setup passed. |
| Planning-file update patch expected a missing section | 1 | Inspected the files and applied a narrower patch matching their actual structure. |

### Phase 8: Apply the 2026-09-02 comment export
- [x] Add a fourth `extreme` start quality and rebalance run-level start counts.
- [x] Redraw the scaling comparison as connected markers on a shared axis.
- [x] Replace per-chain MIF traces with smoothed group curves and add a
      convergence-speed table in both sections.
- [x] Repair the NaN convergence-speed statistic.
- [x] Apply four-significant-digit formatting throughout, with log likelihoods
      at two decimal places.
- [x] Replace the stale release-validator sentinel that blocked publication.
- [x] Confirm the author accepts the log-likelihood formatting exception.
      Confirmed 2026-09-02: log likelihoods stay at two decimal places.
- [x] Make the precision comparison render float64 first, so the published
      document is never the float32 diagnostic.
- [ ] Run the float64 and float32 level-2 renders on the allocated GPU.
- **Status:** implementation complete; render pending.
