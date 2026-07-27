#!/bin/bash
source /apps/anaconda3/etc/profile.d/conda.sh
conda activate py313

# Override the Mac-specific python path baked into _quarto.yml.
export QUARTO_PYTHON="$(command -v python)"

export PATH=$HOME/.local/quarto/quarto-1.4.557/bin:$PATH
export QUARTO_SHARE_PATH=$HOME/.local/quarto/quarto-1.4.557/share
export QUARTO_DENO=$HOME/.local/quarto/quarto-1.4.557/bin/tools/x86_64/deno

mkdir -p /tmp/runtime-$USER /tmp/deno-$USER /tmp/tmpdir-$USER
export XDG_RUNTIME_DIR=/tmp/runtime-$USER
export DENO_DIR=/tmp/deno-$USER
export TMPDIR=/tmp/tmpdir-$USER

# Select the QMD's GPU path before its first import of JAX. Callers may
# override the run level or force-recompute setting on the command line.
export DAPHNIA_USE_GPU=1
export DAPHNIA_RUN_LEVEL="${DAPHNIA_RUN_LEVEL:-3}"
export DAPHNIA_FORCE_RECOMPUTE="${DAPHNIA_FORCE_RECOMPUTE:-0}"

# Let the scheduler/CUDA_VISIBLE_DEVICES select the device. Avoid preallocating
# the full card, which is important on a shared GPU node.
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
unset JAX_PLATFORMS

# Render from the checkout containing this wrapper, regardless of where the
# repository was cloned.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

nvidia-smi 2>&1 | head -10
quarto render daphnia_tut.qmd -M embed-resources:false
render_status=$?
echo "---RENDER: exit=$render_status at $(date)---"
if [ "$render_status" -ne 0 ]; then
  ls -la daphnia_tut.html daphnia_tut_files/ 2>&1
  exit "$render_status"
fi

# The cluster render deliberately leaves images external to avoid Quarto/Deno
# memory exhaustion. Inline only those finished images without executing QMD
# code again, then apply the strict release checks.
python make_standalone_html.py \
  daphnia_tut.html daphnia_tut_standalone.html
package_status=$?
if [ "$package_status" -ne 0 ]; then
  echo "---PACKAGE: exit=$package_status at $(date)---"
  exit "$package_status"
fi

python validate_tutorial_html.py \
  daphnia_tut_standalone.html --standalone
validation_status=$?
echo "---VALIDATION: exit=$validation_status at $(date)---"
ls -la daphnia_tut.html daphnia_tut_standalone.html \
  daphnia_tut_files/ 2>&1
exit "$validation_status"
