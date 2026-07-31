#!/usr/bin/env python3
"""Attach the Quarto page dependencies that a failed render left out.

Quarto renders HTML in two stages: pandoc writes the document, then Quarto's
Deno process attaches the page dependencies -- the Bootstrap bundle that carries
both Bootstrap and Quarto's own layout rules, the icon font, the syntax
highlighting theme, and the scripts quarto.js calls into. On the cluster the
Deno stage has segfaulted after the computation finished, and the render script
packages the document anyway rather than discard hours of GPU time. The result
is a complete document that declares Bootstrap grid classes without shipping
Bootstrap, so the sidebar, the code blocks and the column layout all collapse.

This attaches those dependencies to an already-rendered file, taking them from
the ``_files/libs`` directory of the same render. Everything is inlined, so the
output stays self-contained. Re-running is a no-op.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import re
import sys

# Injected into <head>, in Quarto's own order: the theme bundle first so the
# document rules that follow can override it.
STYLESHEETS = (
    ("bootstrap/bootstrap.min.css", "quarto-bootstrap"),
    ("bootstrap/bootstrap-icons.css", None),
    ("quarto-html/quarto-syntax-highlighting.css", "quarto-text-highlighting-styles"),
    ("quarto-html/tippy.css", None),
)

# Injected ahead of the after-body script, which constructs Tooltip, ClipboardJS
# and AnchorJS and so needs them defined.
SCRIPTS = (
    "quarto-html/popper.min.js",
    "quarto-html/tippy.umd.min.js",
    "bootstrap/bootstrap.min.js",
    "clipboard/clipboard.min.js",
    "quarto-html/anchor.min.js",
)

HEAD_CLOSE = "</head>"
AFTER_BODY_RE = re.compile(r'<script\s+id\s*=\s*"quarto-html-after-body"')
# Pandoc leaves the table of contents in the document body; Quarto moves it into
# the margin sidebar and wires up the scroll-spy classes quarto.js watches.
TOC_RE = re.compile(r'<nav id="TOC"[^>]*>.*?</nav>', flags=re.DOTALL)
TOC_TARGET = '<div id="quarto-toc-target"></div>'
TOC_LINK_RE = re.compile(r'<a href="(#[^"]+)"( id="[^"]*")?>')
# bootstrap-icons.css points at the font file beside it.
ICON_FONT_RE = re.compile(r'url\(\s*(["\']?)\./bootstrap-icons\.woff[^)"\']*\1\s*\)')
# Only the injected <link> carries this; quarto.js refers to it as
# "link#quarto-bootstrap", which does not match.
MARKER = 'id="quarto-bootstrap"'


def _read(libs: Path, relative: str) -> str:
    path = libs / relative
    if not path.is_file():
        raise FileNotFoundError(f"Missing Quarto dependency: {path}")
    return path.read_text(encoding="utf-8")


def _inline_icon_font(libs: Path, css: str) -> str:
    font = libs / "bootstrap" / "bootstrap-icons.woff"
    if not font.is_file():
        raise FileNotFoundError(f"Missing icon font: {font}")
    encoded = base64.b64encode(font.read_bytes()).decode("ascii")
    return ICON_FONT_RE.sub(f'url("data:font/woff;base64,{encoded}")', css)


def _stylesheet_tag(libs: Path, relative: str, element_id: str | None) -> str:
    css = _read(libs, relative)
    if relative.endswith("bootstrap-icons.css"):
        css = _inline_icon_font(libs, css)
    if element_id == "quarto-bootstrap":
        # quarto.js reads the colour mode off link#quarto-bootstrap, so this one
        # has to stay a <link> for the selector to match.
        encoded = base64.b64encode(css.encode("utf-8")).decode("ascii")
        return (
            f'<link href="data:text/css;base64,{encoded}" rel="stylesheet" '
            f'id="{element_id}" data-mode="light">'
        )
    attribute = f' id="{element_id}"' if element_id else ""
    return f'<style type="text/css"{attribute}>\n{css}\n</style>'


def _script_tag(libs: Path, relative: str) -> str:
    source = _read(libs, relative)
    if "</script" in source.lower():
        raise ValueError(f"{relative} cannot be inlined verbatim")
    return f'<script type="text/javascript">\n{source}\n</script>'


def _relocate_toc(html: str) -> str:
    if TOC_TARGET not in html:
        return html
    match = TOC_RE.search(html)
    if match is None:
        return html

    first = True

    def link(m: re.Match[str]) -> str:
        nonlocal first
        target, element_id = m.group(1), m.group(2) or ""
        css = "nav-link active" if first else "nav-link"
        first = False
        return f'<a href="{target}"{element_id} class="{css}" data-scroll-target="{target}">'

    nav = match.group(0)
    nav = nav.replace('<nav id="TOC"', '<nav id="TOC" class="toc-active"', 1)
    nav = TOC_LINK_RE.sub(link, nav)
    return html.replace(match.group(0), "", 1).replace(TOC_TARGET, nav, 1)


def attach(html_path: Path, libs: Path) -> bool:
    html = html_path.read_text(encoding="utf-8")
    if MARKER in html:
        return False

    head_at = html.find(HEAD_CLOSE)
    if head_at < 0:
        raise ValueError(f"No {HEAD_CLOSE} in {html_path}")
    styles = "\n".join(
        _stylesheet_tag(libs, relative, element_id)
        for relative, element_id in STYLESHEETS
    )
    html = f"{html[:head_at]}{styles}\n{html[head_at:]}"

    after_body = AFTER_BODY_RE.search(html)
    if after_body is None:
        raise ValueError(f"No quarto-html-after-body script in {html_path}")
    scripts = "\n".join(_script_tag(libs, relative) for relative in SCRIPTS)
    at = after_body.start()
    html = f"{html[:at]}{scripts}\n{html[at:]}"

    html_path.write_text(_relocate_toc(html), encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "html",
        nargs="?",
        type=Path,
        default=Path("daphnia_tut_pypomp.html"),
        help="rendered HTML to repair in place (default: daphnia_tut_pypomp.html)",
    )
    parser.add_argument(
        "--libs",
        type=Path,
        default=Path("daphnia_tut_pypomp_files/libs"),
        help="Quarto _files/libs directory from the same render",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report whether the dependencies are attached, changing nothing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        attached = MARKER in args.html.read_text(encoding="utf-8")
        print(
            f"Quarto dependencies {'attached' if attached else 'MISSING'}: {args.html}"
        )
        return 0 if attached else 1

    if not attach(args.html, args.libs):
        print(f"Already attached, nothing to do: {args.html}")
        return 0
    size_mb = args.html.stat().st_size / (1024 * 1024)
    print(f"Quarto dependencies attached: {args.html} ({size_mb:.2f} MiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
