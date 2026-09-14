## PanelPOMP data analysis: An ecological experiment with four interacting species

This tutorial introduces the statistical models and methods used for the article: *Mechanistic models for panel data: Analysis of ecological experiments with four interacting species* ([https://arxiv.org/abs/2506.04508](https://arxiv.org/abs/2506.04508)).
The article source code is available on [GitHub](https://github.com/Megumiybb/Daphnia-ms) and [Zenodo](https://doi.org/10.5281/zenodo.15595669).
This tutorial does not reproduce all the results in the article.
Instead, it focuses on guiding the reader through issues involved in the practical implementation of the data analysis, providing step-by-step guidance for implementing Panel Iterated Filtering (PIF) and Marginalized Panel Iterated Filtering (MPIF) methods.

**Status: complete.** All three documents below are rendered from the sources in this repository and are the final versions.

* The [R version of the tutorial](R-code) uses the R package [`panelPomp`](https://github.com/panelPomp-org). It is designed to run on a multi-core CPU computer.
  The rendered document is [`daphnia_tut_R.html`](https://pypomp.github.io/Daphnia-tutorial/R-code/daphnia_tut_R.html).

* The [Python version of the tutorial](Python-code) uses the Python package [`pypomp`](https://github.com/pypomp). It is designed to run on a GPU, but will also run on a multi-core CPU.
  The rendered document is [`daphnia_tut_pypomp.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp.html), covering model construction, PIF and MPIF estimation, and the four diagnostics.
  A second document, [`daphnia_tut_pypomp_advanced.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp_advanced.html), goes further. It is a GPU-only, double-precision, run-level-3 render that compares float32 with float64, compares MIF searches from medium, poor and extreme starting points, times PIF against MPIF, reports 95% Monte Carlo adjusted profile intervals, and introduces `pypomp`'s `bake` and `stew` computation archives with measured timings and reliability checks. A companion [`daphnia_tut_pypomp_advanced_float32.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_pypomp_advanced_float32.html) is the same document rendered in single precision, kept as a diagnostic.

The two languages give the same models, starting values and algorithmic settings, so their results agree up to Monte Carlo error.
Two differences are worth knowing before comparing numbers. Random number streams cannot be made to correspond between `panelPomp` and `pypomp`, so individual searches differ even where the method is identical.
Also, note that R `pomp` computes in double precision while JAX defaults to single, so the Python tutorials set `JAX_ENABLE_X64=1`; without it a particle filter can return log-likelihoods that are not merely imprecise but impossible.
For some Pypomp applications, 32-bit precision has been found to be sufficient, but for this example it is necessary to use 64-bit.

### Reproducing the tutorials
The R version needs `pomp`, `panelPomp` and `tidyverse`; see
[`R-code`](R-code).

The Python versions were produced with exact Pypomp revisions. The advanced tutorial requires Pypomp 1.0.2 at commit `2983c60` and stops with an error if a different build is imported; `daphnia_tut_pypomp.qmd` was written against 1.0.0 at `232180a` and does not check, so verify it yourself.
Three files reproduce either Python document: its `.qmd` source in `Python-code/`, `Python-code/bib-daphnia.bib` and `data/Mesocosmdata.xls`, plus Quarto and the pinned Pypomp checkout.
Point Quarto at the right interpreter with `QUARTO_PYTHON`.
See [`Python-code`](Python-code) for the exact commits, the GPU settings, the run levels and the render scripts.

Source code for this tutorial is at <https://github.com/pypomp/Daphnia-tutorial>.
