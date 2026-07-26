# PanelPOMP Data Analysis Tutorial

This repository contains tutorial materials for the article: *Mechanistic models for panel data: Analysis of ecological experiments with four interacting species* ([https://arxiv.org/abs/2506.04508](https://arxiv.org/abs/2506.04508)).
The article source code is avaialble on [GitHub](https://github.com/Megumiybb/Daphnia-ms) and [Zenodo](https://doi.org/10.5281/zenodo.15595669).
This tutorial does not reproduce all the results in the article.
Instead, it focuses on guiding the reader through issues involved in the practical implementation of the data analysis, providing step-by-step guidance for implementing Panel Iterated Filtering (PIF) and Marginalized Panel Iterated Filtering (MPIF) methods.
There are two versions:

* The [R version](R-code) uses the R package [`panelPomp`](https://github.com/panelPomp-org). It is designed to run on a multi-core CPU computer. 

* The [Python version](Python-code) uses the Python package [`pypomp`](https://github.com/pypomp). It is designed to run on a GPU, but will also run on a multi-core CPU.


