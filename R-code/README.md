## PanelPOMP data analysis in R: A four-species ecological system

**Status: complete.** The rendered tutorial is
[`daphnia_tut_R.html`](https://pypomp.github.io/Daphnia-tutorial/R-code/daphnia_tut_R.html).
The source is `daphnia_tut_R.qmd`; `Makefile` renders it and `data/` holds the
Excel data and the two CSV extracts it reads.

### Prerequisites

Before starting the R version of this tutorial, ensure you have the following R packages installed:

```r
install.packages(c("pomp", "panelPomp", "tidyverse"))
```

### Tutorial Contents

1. **PanelPOMP Model Setup**: How to specify a mechanistic model with shared and unit-specific parameters
2. **Panel Iterated Filtering**: Implementation of the PIF algorithm for likelihood maximization
3. **Parameter Estimation**: Strategies for multi-stage optimization with tempering
4. **Profile Likelihood**: Computing confidence intervals using the MCAP algorithm
5. **Model Diagnostics**: Simulation studies and residual analysis

**Note:** Some computationally intensive examples may require adjustment of `run_level` parameters:
- Level 1: Quick debugging (~minutes)
- Level 2: Local computation (~1 hour on 36 cores)
- Level 3: Full estimation (~40 hours on 36 cores)

The R and Python tutorials use independent run-level definitions; these levels
do not correspond to the Python ones.
