#!/bin/bash
# Run level 2, forcing recomputation, on a GPU node.
#
# The run level is set here rather than on the grid_run command line because a
# batch job does not reliably inherit the submitting shell's environment; if it
# did not, render_gpu.sh would fall back to its default of run level 3.
export DAPHNIA_RUN_LEVEL=2
export DAPHNIA_FORCE_RECOMPUTE=1

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "---LEVEL: DAPHNIA_RUN_LEVEL=$DAPHNIA_RUN_LEVEL, "\
"DAPHNIA_FORCE_RECOMPUTE=$DAPHNIA_FORCE_RECOMPUTE at $(date)---"
exec ./render_gpu.sh
