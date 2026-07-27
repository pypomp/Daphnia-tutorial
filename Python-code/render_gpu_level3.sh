#!/bin/bash
# Run level 3, forcing recomputation, on a GPU node.
#
# The run level is set here rather than on the grid_run command line because a
# batch job does not reliably inherit the submitting shell's environment.
export DAPHNIA_RUN_LEVEL=3
export DAPHNIA_FORCE_RECOMPUTE=1

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Quarto's Deno process segfaulted during HTML assembly on 27 July 2026 with a
# stale cache present. Clearing it is cheap insurance; Quarto repopulates it.
rm -rf "/tmp/deno-$USER"

echo "---LEVEL: DAPHNIA_RUN_LEVEL=$DAPHNIA_RUN_LEVEL, "\
"DAPHNIA_FORCE_RECOMPUTE=$DAPHNIA_FORCE_RECOMPUTE at $(date)---"
exec ./render_gpu.sh
