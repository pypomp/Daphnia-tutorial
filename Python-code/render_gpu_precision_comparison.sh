#!/bin/bash
# Render the complete advanced tutorial twice in separate processes.
# The float32 render is retained as a diagnostic artifact. The second render
# uses float64 and becomes the standard document used by later work.

set -u

DOC="${DAPHNIA_DOC:-daphnia_tut_pypomp_advanced}"
case "$DOC" in
  *[!A-Za-z0-9_-]*|'')
    echo "Invalid document stem: $DOC" >&2
    exit 1
    ;;
esac

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if [ ! -f "$DOC.qmd" ]; then
  echo "No such tutorial: $SCRIPT_DIR/$DOC.qmd" >&2
  exit 1
fi

previous_html=""
had_previous=0
comparison_complete=0
if [ -f "$DOC.html" ]; then
  previous_html="$(mktemp "/tmp/${DOC}.before-precision.XXXXXX.html")" || exit 1
  cp -p "$DOC.html" "$previous_html" || exit 1
  had_previous=1
fi

restore_previous() {
  if [ "$comparison_complete" -eq 0 ]; then
    if [ "$had_previous" -eq 1 ] && [ -f "$previous_html" ]; then
      cp -p "$previous_html" "$DOC.html"
      echo "---RESTORED: pre-comparison $DOC.html---" >&2
    elif [ "$had_previous" -eq 0 ] && [ -f "$DOC.html" ]; then
      rm -f "$DOC.html"
      echo "---RESTORED: no standard HTML existed before comparison---" >&2
    fi
  fi
  if [ -n "$previous_html" ] && [ -f "$previous_html" ]; then
    rm -f "$previous_html"
  fi
}
trap restore_previous EXIT
trap 'exit 1' HUP INT TERM

echo "---PRECISION COMPARISON: complete float32 run---"
float32_status=0
if DAPHNIA_DOC="$DOC" \
   DAPHNIA_RUN_LEVEL=2 \
   DAPHNIA_FORCE_RECOMPUTE=1 \
   DAPHNIA_USE_CPU=0 \
   DAPHNIA_DOUBLE_PRECISION=0 \
   ./render_gpu.sh; then
  if ! cp -p "$DOC.html" "${DOC}_float32.html"; then
    float32_status=1
  fi
else
  float32_status=$?
  echo "---FLOAT32 DIAGNOSTIC FAILED: continuing to the required float64 run---" >&2
fi

echo "---PRECISION COMPARISON: fresh complete float64 run---"
DAPHNIA_DOC="$DOC" \
DAPHNIA_RUN_LEVEL=2 \
DAPHNIA_FORCE_RECOMPUTE=1 \
DAPHNIA_USE_CPU=0 \
DAPHNIA_DOUBLE_PRECISION=1 \
./render_gpu.sh || exit 1
cp -p "$DOC.html" "${DOC}_float64.html" || exit 1

comparison_complete=1
if [ "$float32_status" -eq 0 ]; then
  echo "Float32 diagnostic: ${DOC}_float32.html"
else
  echo "Float32 diagnostic: unavailable because the diagnostic run failed" >&2
fi
echo "Float64 comparison: ${DOC}_float64.html"
echo "Standard output (float64): $DOC.html"

if [ "$float32_status" -ne 0 ]; then
  exit "$float32_status"
fi
