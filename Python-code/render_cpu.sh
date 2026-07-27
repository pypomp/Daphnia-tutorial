#!/bin/bash
source /apps/anaconda3/etc/profile.d/conda.sh
conda activate py313

# Override the Mac-specific python path baked into _quarto.yml.
export QUARTO_PYTHON=$(which python)

# Quarto paths (bundled deno 1.37.2 — newer deno hits CagedHeap OOM on this cluster)
export PATH=$HOME/.local/quarto/quarto-1.4.557/bin:$PATH
export QUARTO_SHARE_PATH=$HOME/.local/quarto/quarto-1.4.557/share
export QUARTO_DENO=$HOME/.local/quarto/quarto-1.4.557/bin/tools/x86_64/deno

# Runtime / scratch dirs (compute nodes lack /run/user/$UID)
mkdir -p /tmp/runtime-$USER /tmp/deno-$USER /tmp/tmpdir-$USER
export XDG_RUNTIME_DIR=/tmp/runtime-$USER
export DENO_DIR=/tmp/deno-$USER
export TMPDIR=/tmp/tmpdir-$USER

# JAX: avoid preallocation; use all granted SGE cores
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
export OMP_NUM_THREADS=${NSLOTS:-1}
export MKL_NUM_THREADS=${NSLOTS:-1}
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=true intra_op_parallelism_threads=${NSLOTS:-1}"
export JAX_PLATFORMS=cpu

cd ~/Documents/Rpomp-Pypomp/PanelPomp-Python

# embed-resources:false avoids the deno HTML-bundling segfault.
# Non-zero exit code is harmless: HTML is fully written before any post-render cleanup crash.
quarto render daphnia_tut.qmd -M embed-resources:false
echo "---DONE: exit=$? at $(date)---"
ls -la daphnia_tut.html daphnia_tut_files/ 2>&1

