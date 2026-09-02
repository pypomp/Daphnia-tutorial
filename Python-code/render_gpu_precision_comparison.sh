#!/bin/bash
# Render the complete advanced tutorial twice, in separate processes.
#
# JAX fixes its precision when it initialises, so one process cannot do both.
# float64 runs FIRST and is the render that gets published; float32 follows as
# a diagnostic and is never left in place as the standard document.
#
#   ${DOC}_float64.html   the float64 render
#   ${DOC}_float32.html   the float32 diagnostic
#   ${DOC}.html           the published document, always the float64 render
#
# The exit status reports the float32 diagnostic: a non-zero exit with a
# "Float64 (published)" line means the required render succeeded and only the
# diagnostic was lost.

set -u

DOC="${DAPHNIA_DOC:-daphnia_tut_pypomp_advanced}"
RUN_LEVEL="${DAPHNIA_RUN_LEVEL:-2}"
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
float64_published=0
if [ -f "$DOC.html" ]; then
  previous_html="$(mktemp "/tmp/${DOC}.before-precision.XXXXXX.html")" || exit 1
  cp -p "$DOC.html" "$previous_html" || exit 1
  had_previous=1
fi

finish() {
  # The float32 pass runs second, so on success it leaves a float32 document
  # in $DOC.html. The published document must be float64 either way.
  if [ "$float64_published" -eq 1 ] && [ -f "${DOC}_float64.html" ]; then
    cp -p "${DOC}_float64.html" "$DOC.html"
  elif [ "$had_previous" -eq 1 ] && [ -f "$previous_html" ]; then
    cp -p "$previous_html" "$DOC.html"
    echo "---RESTORED: pre-comparison $DOC.html---" >&2
  elif [ -f "$DOC.html" ]; then
    rm -f "$DOC.html"
    echo "---RESTORED: no standard HTML existed before comparison---" >&2
  fi
  if [ -n "$previous_html" ] && [ -f "$previous_html" ]; then
    rm -f "$previous_html"
  fi
}
trap finish EXIT
trap 'exit 1' HUP INT TERM

echo "---PRECISION COMPARISON: complete float64 run (published)---"
if ! DAPHNIA_DOC="$DOC" \
     DAPHNIA_RUN_LEVEL="$RUN_LEVEL" \
     DAPHNIA_FORCE_RECOMPUTE=1 \
     DAPHNIA_USE_CPU=0 \
     DAPHNIA_DOUBLE_PRECISION=1 \
     ./render_gpu.sh; then
  echo "---FLOAT64 RENDER FAILED: nothing published, float32 not attempted---" >&2
  exit 1
fi
cp -p "$DOC.html" "${DOC}_float64.html" || exit 1
float64_published=1

echo "---PRECISION COMPARISON: complete float32 run (diagnostic)---"
float32_status=0
if DAPHNIA_DOC="$DOC" \
   DAPHNIA_RUN_LEVEL="$RUN_LEVEL" \
   DAPHNIA_FORCE_RECOMPUTE=1 \
   DAPHNIA_USE_CPU=0 \
   DAPHNIA_DOUBLE_PRECISION=0 \
   ./render_gpu.sh; then
  cp -p "$DOC.html" "${DOC}_float32.html" || float32_status=1
else
  float32_status=$?
  echo "---FLOAT32 DIAGNOSTIC FAILED: the float64 document is unaffected---" >&2
fi

echo "Float64 (published): ${DOC}_float64.html, copied to $DOC.html"
if [ "$float32_status" -eq 0 ]; then
  echo "Float32 diagnostic:  ${DOC}_float32.html"
else
  echo "Float32 diagnostic:  unavailable, the diagnostic run failed" >&2
fi

exit "$float32_status"
