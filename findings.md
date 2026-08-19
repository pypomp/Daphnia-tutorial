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

## Resources

- `Python-code/daphnia_tut_pypomp_advanced.qmd`
- `Python-code/daphnia_tut_pypomp.qmd`
- `R-code/daphnia_tut_R.qmd`
- `Python-code/validate_tutorial_html.py`
- `Python-code/render_gpu.sh`
- `Python-code/README.md`
- `/Users/ybb/Downloads/Research/Rpomp-Pypomp/PanelPomp-Python/run_commend.txt`
