

## PanelPOMP data analysis in Python: A four-species ecological system

### Prerequisites

To run the code in the Python version of this tutorial, ensure you have Pypomp installed:

```
pip install pypomp 
```

This will also install JAX. 

### Tutorial Contents

The [tutorial](daphnia-tut.html) covers:

1. **PanelPOMP Model Setup**: How to specify a mechanistic model with shared and unit-specific parameters
2. **Panel Iterated Filtering**: Implementation of the PIF algorithm for likelihood maximization
3. **Parameter Estimation**: Strategies for multi-stage optimization with tempering
4. **Profile Likelihood**: Computing confidence intervals using the MCAP algorithm
5. **Model Diagnostics**: Simulation studies and residual analysis

**Note:** Some computationally intensive examples may require adjustment of `run_level` parameters:
- Level 1: Quick debugging (~minutes)
- Level 2: Local computation 
- Level 3: Full estimation 

