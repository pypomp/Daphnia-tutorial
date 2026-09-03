#!/usr/bin/env python3
"""Execute every Python chunk of a tutorial at run level 1, on CPU.

This is a structural smoke test, not an analysis. It runs the same code the
render runs, in the same order and in one namespace, so a NameError, a bad
Pypomp call or a broken chunk fence is found in minutes on a laptop instead of
an hour into a GPU batch job. It does not use Quarto and does not write HTML.

    python smoke_test.py                             # daphnia_tut_pypomp.qmd
    python smoke_test.py daphnia_tut_pypomp_advanced.qmd

Numerical gates are expected to FAIL at run level 1; that is what run level 1
means. Only an exception is a failure of this script.

The cache is written to a scratch directory so that a smoke test can never be
mistaken for, or overwrite, a scientific render.

Two render-time provenance gates are relaxed here and only here: the advanced
tutorial's requirement of a CUDA GPU backend, and its comparison of the
imported Pypomp build against the pinned one. Neither is about whether the code
runs, which is the only question this script asks, and enforcing them would
make the advanced document impossible to smoke test on a laptop at all. What
was actually imported is printed in the banner, so a run against the wrong
Pypomp is visible rather than silent. `render_gpu.sh` and
`validate_tutorial_html.py` still enforce both gates for anything published.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ["DAPHNIA_RUN_LEVEL"] = "1"
os.environ["DAPHNIA_USE_GPU"] = "0"
os.environ["DAPHNIA_FORCE_RECOMPUTE"] = "1"
os.environ.setdefault(
    "DAPHNIA_CACHE_ROOT",
    str(Path(tempfile.gettempdir()) / "daphnia-smoke-cache"),
)
Path(os.environ["DAPHNIA_CACHE_ROOT"]).mkdir(parents=True, exist_ok=True)

HERE = Path(__file__).resolve().parent
QMD = HERE / (sys.argv[1] if len(sys.argv) > 1 else "daphnia_tut_pypomp.qmd")
if not QMD.is_file():
    raise SystemExit(f"No such tutorial: {QMD}")
os.chdir(HERE)


def python_chunks(path: Path) -> list[tuple[str, int, str]]:
    """Return (label, first line, body) for each ```{python} chunk.

    Chunk-option lines are replaced by blanks rather than dropped so that a
    traceback line number still points at the right line of the QMD.
    """
    chunks: list[tuple[str, int, str]] = []
    body: list[str] = []
    inside = False
    label = None
    start = 0
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not inside and line.startswith("```{python}"):
            inside, body, start, label = True, [], lineno, None
            continue
        if inside and line.startswith("```"):
            chunks.append((label or f"chunk@{start}", start, "\n".join(body)))
            inside = False
            continue
        if inside:
            match = re.match(r"^#\|\s*label:\s*(\S+)", line)
            if match:
                label = match.group(1)
            body.append("" if line.startswith("#|") else line)
    if inside:
        raise SystemExit(f"unterminated ```{{python}} chunk opened at line {start}")
    return chunks


# (guard source, replacement) pairs. Each is matched exactly; a guard whose
# wording has drifted is reported rather than silently skipped, because a
# relaxation that stops applying would turn this script into a no-op on the
# document it most needs to check.
RELAXATIONS = (
    (
        'if not use_gpu:\n'
        '    raise RuntimeError(\n'
        '        "This advanced tutorial requires a CUDA GPU. Set DAPHNIA_USE_GPU=1."\n'
        '    )',
        'if not use_gpu:\n'
        '    pass  # relaxed by smoke_test.py',
    ),
    (
        'if jax.default_backend() != "gpu":\n'
        '    raise RuntimeError(\n'
        '        "No CUDA GPU backend is active. This render will not fall back to CPU."\n'
        '    )',
        'if jax.default_backend() != "gpu":\n'
        '    pass  # relaxed by smoke_test.py',
    ),
    (
        'if CACHE_METADATA["pypomp_commit"] != EXPECTED_PYPOMP_COMMIT:',
        'if False:  # pin comparison relaxed by smoke_test.py\n'
        '    _ = EXPECTED_PYPOMP_COMMIT\n'
        'if False:',
    ),
    (
        'if pp.__version__ != EXPECTED_PYPOMP_VERSION:',
        'if False:  # pin comparison relaxed by smoke_test.py\n'
        '    _ = EXPECTED_PYPOMP_VERSION\n'
        'if False:',
    ),
)


def relax_render_gates(body: str) -> tuple[str, int]:
    """Neutralise the GPU and Pypomp-pin gates in one chunk body."""
    applied = 0
    for guard, replacement in RELAXATIONS:
        if guard in body:
            body = body.replace(guard, replacement)
            applied += 1
    return body, applied


def main() -> int:
    chunks = python_chunks(QMD)
    relaxed = 0
    rebuilt = []
    for label, lineno, body in chunks:
        body, applied = relax_render_gates(body)
        relaxed += applied
        rebuilt.append((label, lineno, body))
    chunks = rebuilt

    print(f"{QMD.name}: {len(chunks)} Python chunks, run_level=1, CPU", flush=True)
    if relaxed:
        print(f"  {relaxed} render-time gate(s) relaxed for this run; "
              "this is not a render.", flush=True)
    if 0 < relaxed < len(RELAXATIONS):
        # Every guard is matched by its exact source. A partial match means one
        # has been reworded, and the unmatched one will stop this document.
        print(f"  WARNING: only {relaxed} of {len(RELAXATIONS)} known gates "
              "matched; a guard has probably been reworded.", flush=True)
    # Resolve Pypomp without importing it. Importing pulls in JAX, which fixes
    # the backend and the x64 flag before the setup chunk has set them, and the
    # document then correctly refuses to run.
    try:
        from importlib.metadata import version as _dist_version  # noqa: PLC0415
        from importlib.util import find_spec  # noqa: PLC0415
        spec = find_spec("pypomp")
        origin = spec.origin if spec is not None else "not found"
        print(f"  pypomp {_dist_version('pypomp')} from {origin}", flush=True)
    except Exception as exc:  # pragma: no cover - reported, not fatal
        print(f"  pypomp could not be resolved: {exc}", flush=True)
    print(flush=True)
    namespace: dict = {"__name__": "__main__"}
    started = time.time()
    for index, (label, lineno, body) in enumerate(chunks, 1):
        chunk_started = time.time()
        try:
            exec(compile(body, f"<{label}>", "exec"), namespace)
        except Exception:
            print(f"\nFAILED at chunk {index}/{len(chunks)} "
                  f"'{label}' ({QMD.name} line {lineno})\n")
            traceback.print_exc()
            return 1
        print(f"  {index:2d}/{len(chunks)}  {label:<40s} "
              f"{time.time() - chunk_started:7.1f}s", flush=True)
    print(f"\nAll {len(chunks)} chunks executed in "
          f"{time.time() - started:.0f}s. Structure is sound; numerical gates "
          "at run level 1 are not meaningful.")
    # The document records what it actually imported. Print it, since the pin
    # comparison was relaxed above and this is the only remaining record.
    metadata = namespace.get("CACHE_METADATA")
    if isinstance(metadata, dict):
        print(f"Ran against Pypomp {metadata.get('pypomp_version')} at "
              f"{metadata.get('pypomp_commit')}, backend "
              f"{metadata.get('backend')}, x64 "
              f"{metadata.get('jax_enable_x64')}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
