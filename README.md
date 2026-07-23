# PanelPOMP Data Analysis Tutorial

This repository contains the tutorial materials (Supplement 2) for the article: *Mechanistic models for panel data: Analysis of ecological experiments with four interacting species* ([https://arxiv.org/abs/2506.04508](https://arxiv.org/abs/2506.04508)).

The tutorial provides step-by-step guidance for implementing Panel Iterated Filtering (PIF) and Marginalized Panel Iterated Filtering (MPIF) method using the `panelPomp` R/Python package.

## Prerequisites

Before starting the tutorial, ensure you have the following R packages installed:

```r
install.packages(c("pomp", "panelPomp", "tidyverse"))
```

## Tutorial Contents

The tutorial (`tut.html`) covers:

1. **PanelPOMP Model Setup**: How to specify a mechanistic model with shared and unit-specific parameters
2. **Panel Iterated Filtering**: Implementation of the PIF algorithm for likelihood maximization
3. **Parameter Estimation**: Strategies for multi-stage optimization with tempering
4. **Profile Likelihood**: Computing confidence intervals using the MCAP algorithm
5. **Model Diagnostics**: Simulation studies and residual analysis

**Note:** Some computationally intensive examples may require adjustment of `run_level` parameters:
- Level 1: Quick debugging (~minutes)
- Level 2: Local computation (~1 hour on 36 cores)
- Level 3: Full estimation (~40 hours on 36 cores)

This tutorial accompanies the main analysis repository. For the complete analysis pipeline, data files, and manuscript source, see:

- **GitHub**: https://github.com/Megumiybb/Daphnia-ms
- **Zenodo**: https://doi.org/10.5281/zenodo.15595669
