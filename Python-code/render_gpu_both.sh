#!/bin/bash
# Render both Python tutorials in one GPU allocation, one after the other.
#
# They must not run concurrently. DENO_DIR, TMPDIR and Quarto's .quarto/
# directory are per-user rather than per-job, and each level wrapper clears the
# Deno cache as it starts, so a second job would pull that cache out from under
# a render already in flight. Two double-precision jobs also contend for the
# card. Running them in sequence inside a single allocation is the safe way to
# get both documents from one submission.
#
#   ./render_gpu_both.sh 3            # run level as an argument, preferred
#   DAPHNIA_RUN_LEVEL=3 ./render_gpu_both.sh
#
# Prefer the argument for batch submission. A batch job does not reliably
# inherit the submitting shell's environment, and if DAPHNIA_RUN_LEVEL were
# dropped this would quietly fall back to level 2 and burn the allocation on
# the wrong run.
#
# Each document goes through the full chain in render_gpu.sh: quarto render,
# make_standalone_html.py to inline the figures, embed_quarto_deps.py to attach
# the Quarto page dependencies, then the --check gate and the release
# validator. Only a document that passes all of it is moved into place, so a
# published file here is always self-contained and correctly styled.
#
# The second document is attempted even if the first fails, because the
# allocation is already paid for. The exit status reports whether both
# succeeded.

LEVEL="${1:-${DAPHNIA_RUN_LEVEL:-2}}"
WRAPPER="./render_gpu_level${LEVEL}.sh"
DOCS="daphnia_tut_pypomp daphnia_tut_pypomp_advanced"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if [ ! -x "$WRAPPER" ]; then
  echo "No wrapper for run level $LEVEL: $SCRIPT_DIR/$WRAPPER" >&2
  exit 1
fi
for DOC in $DOCS; do
  if [ ! -f "$DOC.qmd" ]; then
    echo "No such tutorial: $SCRIPT_DIR/$DOC.qmd" >&2
    exit 1
  fi
done

started=$(date +%s)
failed=""

for DOC in $DOCS; do
  echo
  echo "=========================================================="
  echo "=== $DOC : run level $LEVEL : start $(date)"
  echo "=========================================================="
  DAPHNIA_DOC="$DOC" "$WRAPPER"
  status=$?
  if [ "$status" -ne 0 ]; then
    failed="$failed $DOC"
    echo "=== $DOC : FAILED (exit=$status) at $(date)"
  else
    echo "=== $DOC : finished at $(date)"
  fi
done

echo
echo "---SUMMARY at $(date), $(( ($(date +%s) - started) / 60 )) min total---"
for DOC in $DOCS; do
  # The same one-line diagnostic embed_quarto_deps.py --check applies: a
  # partial render carries no link#quarto-bootstrap. Done with grep so the
  # summary does not depend on the conda environment the wrappers activate.
  if [ -f "$DOC.html" ] && grep -q 'id="quarto-bootstrap"' "$DOC.html"; then
    size=$(du -h "$DOC.html" | cut -f1)
    # A document can be in place because this run produced it, or because the
    # run failed and render_gpu.sh restored the previous one. Saying which
    # matters: the second is a stale document, not a new result.
    case " $failed " in
      *" $DOC "*) printf '  %-34s unchanged, previous kept  %s\n' "$DOC.html" "$size" ;;
      *)          printf '  %-34s published                 %s\n' "$DOC.html" "$size" ;;
    esac
  else
    printf '  %-34s NOT PUBLISHED\n' "$DOC.html"
  fi
done

if [ -n "$failed" ]; then
  echo "Failed:$failed" >&2
  exit 1
fi
echo "Both tutorials published."
