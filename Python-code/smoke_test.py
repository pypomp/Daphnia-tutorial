#!/usr/bin/env python3
"""Execute every Python chunk of daphnia_tut.qmd at run level 1, on CPU.

This is a structural smoke test, not an analysis. It runs the same code the
render runs, in the same order and in one namespace, so a NameError, a bad
Pypomp call or a broken chunk fence is found in minutes on a laptop instead of
an hour into a GPU batch job. It does not use Quarto and does not write HTML.

    python smoke_test.py

Numerical gates are expected to FAIL at run level 1; that is what run level 1
means. Only an exception is a failure of this script.

The cache is written to a scratch directory so that a smoke test can never be
mistaken for, or overwrite, a scientific render.
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

QMD = Path(__file__).resolve().parent / "daphnia_tut.qmd"
os.chdir(QMD.parent)


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


def main() -> int:
    chunks = python_chunks(QMD)
    print(f"{QMD.name}: {len(chunks)} Python chunks, run_level=1, CPU\n")
    namespace: dict = {"__name__": "__main__"}
    started = time.time()
    for index, (label, lineno, body) in enumerate(chunks, 1):
        chunk_started = time.time()
        try:
            exec(compile(body, f"<{label}>", "exec"), namespace)
        except Exception:
            print(f"\nFAILED at chunk {index}/{len(chunks)} "
                  f"'{label}' (daphnia_tut.qmd line {lineno})\n")
            traceback.print_exc()
            return 1
        print(f"  {index:2d}/{len(chunks)}  {label:<40s} "
              f"{time.time() - chunk_started:7.1f}s")
    print(f"\nAll {len(chunks)} chunks executed in "
          f"{time.time() - started:.0f}s. Structure is sound; numerical gates "
          "at run level 1 are not meaningful.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
