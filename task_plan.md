# Task Plan: Repair advanced Daphnia tutorial validation

## Goal
Produce a staged, evidence-based plan that makes the advanced tutorial numerically trustworthy, scientifically comparable to the R and regular Python tutorials, and reproducibly publishable.

## Current Phase
Phase 1 advanced-QMD corrections complete; cluster rerender not started.

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

## Decisions Made

| Decision | Rationale |
|---|---|
| Fix deterministic defects before spending GPU time | Current float32 and MCAP-level defects can invalidate expensive results. |
| Validate fixed reference vectors before optimization | This separates model/likelihood disagreement from search failure. |
| Treat weak identification separately from computation failure | A scientifically flat profile should not be disguised as an algorithm bug. |
| Use 95% confidence intervals exclusively | This is the user's inferential requirement and must be identical in base and sensitivity fits. |
| Make the document name a wrapper argument | ResearchGrid batch submission may not preserve environment prefixes reliably. |
| Modify only the advanced QMD in this implementation turn | The user requested modification of the singular attached QMD; generated HTML and cluster wrappers remain untouched. |

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| Setup test could not find the QMD from repository root | 1 | Re-ran from `Python-code`, matching the Quarto and ResearchGrid wrapper working directory; setup passed. |
| Planning-file update patch expected a missing section | 1 | Inspected the files and applied a narrower patch matching their actual structure. |
