#!/bin/bash
# Render one tutorial on a cluster GPU node and package it for publication.
#
# Which document is rendered comes from DAPHNIA_DOC (the file stem, no
# extension). The level wrappers beside this script set it along with the run
# level, because a batch job does not reliably inherit the submitting shell's
# environment.
#
#   DAPHNIA_DOC=daphnia_tut_pypomp_advanced ./render_gpu.sh

DOC="${DAPHNIA_DOC:-daphnia_tut_pypomp}"

source /apps/anaconda3/etc/profile.d/conda.sh
conda activate py313
export QUARTO_PYTHON="$(command -v python)"

export PATH=$HOME/.local/quarto/quarto-1.4.557/bin:$PATH
export QUARTO_SHARE_PATH=$HOME/.local/quarto/quarto-1.4.557/share
export QUARTO_DENO=$HOME/.local/quarto/quarto-1.4.557/bin/tools/x86_64/deno

# Compute nodes lack /run/user/$UID.
mkdir -p /tmp/runtime-$USER /tmp/deno-$USER /tmp/tmpdir-$USER
export XDG_RUNTIME_DIR=/tmp/runtime-$USER
export DENO_DIR=/tmp/deno-$USER
export TMPDIR=/tmp/tmpdir-$USER

# Chosen before the QMD's first import of JAX; afterwards it is a silent no-op.
export DAPHNIA_USE_GPU=1
export DAPHNIA_RUN_LEVEL="${DAPHNIA_RUN_LEVEL:-3}"
export DAPHNIA_FORCE_RECOMPUTE="${DAPHNIA_FORCE_RECOMPUTE:-0}"

# Let the scheduler pick the device, and do not reserve the whole card.
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_PYTHON_CLIENT_ALLOCATOR=platform
unset JAX_PLATFORMS

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
if [ ! -f "$DOC.qmd" ]; then
  echo "No such tutorial: $SCRIPT_DIR/$DOC.qmd" >&2
  exit 1
fi

echo "---RENDER: doc=$DOC run_level=$DAPHNIA_RUN_LEVEL start $(date)---"
nvidia-smi 2>&1 | head -10

# Quarto exhausts memory embedding resources on this cluster, so images are
# left external here and inlined below.
quarto render "$DOC.qmd" -M embed-resources:false
render_status=$?
echo "---RENDER: exit=$render_status at $(date)---"

# Quarto's Deno process has segfaulted during HTML assembly *after* the
# document was written, so packaging proceeds regardless of the exit status.
# The checks below decide whether the result is publishable; the exit status
# does not.
if [ ! -f "$DOC.html" ]; then
  echo "---ABORT: no $DOC.html to package at $(date)---" >&2
  exit "${render_status:-1}"
fi

python make_standalone_html.py "$DOC.html" "${DOC}_standalone.html" || exit 1
python embed_quarto_deps.py "${DOC}_standalone.html" \
  --libs "${DOC}_files/libs" || exit 1
echo "---PACKAGE: ok at $(date)---"

# The gate. A dead Deno stage leaves a document that renders as unstyled
# pandoc output; without this it would be published silently.
python embed_quarto_deps.py --check "${DOC}_standalone.html" || exit 1
python validate_tutorial_html.py "${DOC}_standalone.html" --standalone || exit 1

mv "${DOC}_standalone.html" "$DOC.html"
ls -la "$DOC.html"
echo "---PUBLISHED: $DOC.html at $(date)---"
