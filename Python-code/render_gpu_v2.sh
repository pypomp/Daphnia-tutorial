#!/bin/bash
# Render daphnia_tut_v2.qmd (the literal port of R-code/tut.qmd) on a GPU node.
#
# Run level and worker count are exported here rather than passed on the
# grid_run command line, because a batch job does not reliably inherit the
# submitting shell's environment.
#
#   DAPHNIA_RUN_LEVEL   1, 2 or 3.  R's published document uses 2.
#   DAPHNIA_N_WORKERS   stands in for R's getDoParWorkers(). R registers
#                       10 searches per worker in Section 1 and 2 per worker
#                       in Section 2, so this scales the whole job.
export DAPHNIA_RUN_LEVEL="${DAPHNIA_RUN_LEVEL:-3}"
export DAPHNIA_N_WORKERS="${DAPHNIA_N_WORKERS:-36}"
export DAPHNIA_USE_GPU=1

source /apps/anaconda3/etc/profile.d/conda.sh
conda activate py313
export QUARTO_PYTHON="$(command -v python)"

export PATH=$HOME/.local/quarto/quarto-1.4.557/bin:$PATH
export QUARTO_SHARE_PATH=$HOME/.local/quarto/quarto-1.4.557/share
export QUARTO_DENO=$HOME/.local/quarto/quarto-1.4.557/bin/tools/x86_64/deno

mkdir -p /tmp/runtime-$USER /tmp/tmpdir-$USER
export XDG_RUNTIME_DIR=/tmp/runtime-$USER
export TMPDIR=/tmp/tmpdir-$USER
rm -rf "/tmp/deno-$USER"; mkdir -p "/tmp/deno-$USER"
export DENO_DIR=/tmp/deno-$USER

# Do not preallocate the whole card; important on a shared GPU node.
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
unset JAX_PLATFORMS

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "---V2 RENDER: run_level=$DAPHNIA_RUN_LEVEL, workers=$DAPHNIA_N_WORKERS,"\
"start $(date)---"
nvidia-smi 2>&1 | head -10

quarto render daphnia_tut_v2.qmd -M embed-resources:false
status=$?
echo "---RENDER: exit=$status at $(date)---"

# Quarto's Deno process has segfaulted during HTML assembly after the
# computation completed, so package regardless of the exit status.
if [ -f daphnia_tut_v2.html ]; then
  python make_standalone_html.py \
    daphnia_tut_v2.html daphnia_tut_v2_standalone.html
  echo "---PACKAGE: exit=$? at $(date)---"
fi
ls -la daphnia_tut_v2.html daphnia_tut_v2_standalone.html 2>&1
exit "$status"
