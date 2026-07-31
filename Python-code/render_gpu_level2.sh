#!/bin/bash
# Run level 2 on a GPU node, forcing recomputation.
#
# The run level and the document are set here rather than on the grid_run
# command line because a batch job does not reliably inherit the submitting
# shell's environment; if it did not, render_gpu.sh would fall back to its
# defaults.
export DAPHNIA_RUN_LEVEL=2
export DAPHNIA_FORCE_RECOMPUTE=1
export DAPHNIA_DOC="${DAPHNIA_DOC:-daphnia_tut_pypomp}"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Clear a possibly stale Deno cache; Quarto segfaulted during HTML assembly
# on 27 July 2026 with one present. Quarto repopulates it.
rm -rf "/tmp/deno-$USER"

echo "---LEVEL: doc=$DAPHNIA_DOC run_level=$DAPHNIA_RUN_LEVEL at $(date)---"
exec ./render_gpu.sh
