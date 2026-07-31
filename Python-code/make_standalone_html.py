#!/usr/bin/env python3
"""Embed local tutorial images into a standalone HTML file.

The cluster renders with ``embed-resources:false`` to avoid Quarto/Deno memory
failures. This post-processor performs the small remaining job without
re-executing the QMD: it replaces local ``<img src=...>`` references with data
URIs and verifies that no local page resources remain.
"""

from __future__ import annotations

import argparse
import base64
from html.parser import HTMLParser
import mimetypes
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit


IMG_SRC_RE = re.compile(
    r"(?P<prefix><img\b[^>]*?\bsrc\s*=\s*)"
    r"(?P<quote>[\"'])(?P<value>[^\"']+)(?P=quote)",
    flags=re.IGNORECASE,
)
RESOURCE_ATTR = {"img": "src", "script": "src", "link": "href"}


def _is_local_reference(value: str) -> bool:
    value = value.strip()
    if not value or value.startswith(("#", "data:")):
        return False
    scheme = urlsplit(value).scheme.lower()
    return scheme not in {
        "http", "https", "mailto", "javascript", "tel",
    }


class _ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.local_resources: list[tuple[str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attr_name = RESOURCE_ATTR.get(tag.lower())
        if attr_name is None:
            return
        attr_map = dict(attrs)
        value = attr_map.get(attr_name)
        if value is not None and _is_local_reference(value):
            self.local_resources.append((tag.lower(), value))


def _resolve_local_image(html_path: Path, reference: str) -> Path:
    parsed = urlsplit(reference)
    if parsed.scheme and parsed.scheme.lower() != "file":
        raise ValueError(f"Unsupported local image scheme: {reference}")
    raw_path = unquote(parsed.path)
    candidate = (
        Path(raw_path).resolve()
        if Path(raw_path).is_absolute()
        else (html_path.parent / raw_path).resolve()
    )
    allowed_root = html_path.parent.resolve()
    if candidate != allowed_root and allowed_root not in candidate.parents:
        raise ValueError(
            f"Refusing to embed an image outside {allowed_root}: {reference}"
        )
    if not candidate.is_file():
        raise FileNotFoundError(
            f"Referenced image does not exist: {reference} -> {candidate}"
        )
    return candidate


def _image_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime not in {
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/svg+xml",
        "image/webp",
    }:
        raise ValueError(f"Unsupported image type for {path}: {mime}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def local_resources(html: str) -> list[tuple[str, str]]:
    parser = _ResourceParser()
    parser.feed(html)
    return parser.local_resources


def build_standalone(input_path: Path, output_path: Path) -> int:
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    if input_path == output_path:
        raise ValueError(
            "Input and output must differ so the original cluster render is preserved."
        )
    html = input_path.read_text(encoding="utf-8")
    embedded = 0

    def replace_image(match: re.Match[str]) -> str:
        nonlocal embedded
        reference = match.group("value")
        if not _is_local_reference(reference):
            return match.group(0)
        image_path = _resolve_local_image(input_path, reference)
        embedded += 1
        quote = match.group("quote")
        return (
            f"{match.group('prefix')}{quote}"
            f"{_image_data_uri(image_path)}{quote}"
        )

    standalone = IMG_SRC_RE.sub(replace_image, html)
    remaining = local_resources(standalone)
    if remaining:
        formatted = ", ".join(f"{tag}:{value}" for tag, value in remaining)
        raise RuntimeError(f"Local resources remain after embedding: {formatted}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(standalone)
        temporary = Path(handle.name)
    os.replace(temporary, output_path)
    return embedded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Embed local images in a rendered tutorial HTML without rerunning Quarto."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path("daphnia_tut_pypomp.html"),
        help="cluster-rendered HTML (default: daphnia_tut_pypomp.html)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path("daphnia_tut_pypomp_standalone.html"),
        help="standalone output HTML (default: daphnia_tut_pypomp_standalone.html)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="only verify that INPUT has no local page resources",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        remaining = local_resources(args.input.read_text(encoding="utf-8"))
        if remaining:
            for tag, value in remaining:
                print(f"LOCAL RESOURCE: {tag} {value}")
            return 1
        print(f"Standalone resource check: PASS ({args.input})")
        return 0

    count = build_standalone(args.input, args.output)
    size_mb = args.output.stat().st_size / (1024 * 1024)
    print(
        f"Standalone HTML written: {args.output} "
        f"({count} images embedded, {size_mb:.2f} MiB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
