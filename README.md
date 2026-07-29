## PanelPOMP data analysis: An ecological experiment with four interacting species

This tutorial introduces the statistical models and methods used for the article: *Mechanistic models for panel data: Analysis of ecological experiments with four interacting species* ([https://arxiv.org/abs/2506.04508](https://arxiv.org/abs/2506.04508)).
The article source code is available on [GitHub](https://github.com/Megumiybb/Daphnia-ms) and [Zenodo](https://doi.org/10.5281/zenodo.15595669).
This tutorial does not reproduce all the results in the article.
Instead, it focuses on guiding the reader through issues involved in the practical implementation of the data analysis, providing step-by-step guidance for implementing Panel Iterated Filtering (PIF) and Marginalized Panel Iterated Filtering (MPIF) methods.

* The [R version of the tutorial](R-code) uses the R package [`panelPomp`](https://github.com/panelPomp-org). It is designed to run on a multi-core CPU computer.
  The rendered document is [`tut.html`](https://pypomp.github.io/Daphnia-tutorial/R-code/tut.html).

* The [Python version of the tutorial](Python-code) uses the Python package [`pypomp`](https://github.com/pypomp). It is designed to run on a GPU, but will also run on a multi-core CPU.
  The rendered document is [`daphnia_tut_v2.html`](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut_v2.html), which follows the R version section by section and reports the same analyses.
  An [extended Python version](https://pypomp.github.io/Daphnia-tutorial/Python-code/daphnia_tut.html) adds numerical validation gates and a discussion of GPU execution.

The two languages give the same models, starting values and algorithmic
settings, so their results agree up to Monte Carlo error. Two differences are
worth knowing before comparing numbers. Random number streams cannot be made to
correspond between `panelPomp` and `pypomp`, so individual searches differ even
where the method is identical. And `pomp` computes in double precision while
JAX defaults to single, so the Python tutorial sets `JAX_ENABLE_X64=1`; without
it a particle filter can return log-likelihoods that are not merely imprecise
but impossible.

### Reproducing the tutorials
The R version needs `pomp`, `panelPomp` and `tidyverse`; see
[`R-code`](R-code).

The Python version pins an exact Pypomp revision and will stop with an error if
a different one is installed. Three files are enough to reproduce it —
`Python-code/daphnia_tut_v2.qmd`, `Python-code/bib-daphnia.bib` and
`data/Mesocosmdata.xls` — plus Quarto and the pinned Pypomp checkout. Point
Quarto at the right interpreter with `QUARTO_PYTHON`. See
[`Python-code`](Python-code) for the exact commit, the GPU settings and the run
levels.

Source code for this tutorial is at <https://github.com/pypomp/Daphnia-tutorial>.
