#!/usr/bin/env python3
"""Validate the rendered Python tutorial before release."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit


VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
RESOURCE_ATTR = {"img": "src", "script": "src", "link": "href"}
REQUIRED_TEXT = (
    "not itself peer-reviewed",
    "Diagnostic 4: Monte Carlo Adjusted Profile",
    "SIRJPF2 specification used here contains only shared parameters",
)


def _is_local_reference(value: str) -> bool:
    value = value.strip()
    if not value or value.startswith(("#", "data:")):
        return False
    return urlsplit(value).scheme.lower() not in {
        "http", "https", "mailto", "javascript", "tel",
    }


class TutorialParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.active_figures: list[str] = []
        self.figure_images: dict[str, int] = {}
        self.local_resources: list[tuple[str, str]] = []
        self.text: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        attr_map = dict(attrs)
        candidate_id = attr_map.get("id")
        classes = set((attr_map.get("class") or "").split())
        figure_id = (
            candidate_id
            if (
                tag == "div"
                and candidate_id
                and candidate_id.startswith("fig-")
                and "quarto-figure" in classes
            )
            else None
        )
        if figure_id:
            self.figure_images.setdefault(figure_id, 0)
            self.active_figures.append(figure_id)
        if tag == "img":
            for active in self.active_figures:
                self.figure_images[active] += 1
        resource_attr = RESOURCE_ATTR.get(tag)
        if resource_attr:
            value = attr_map.get(resource_attr)
            if value is not None and _is_local_reference(value):
                self.local_resources.append((tag, value))
        if tag not in VOID_TAGS:
            self.stack.append((tag, figure_id))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        while self.stack:
            open_tag, figure_id = self.stack.pop()
            if figure_id in self.active_figures:
                self.active_figures.remove(figure_id)
            if open_tag == tag:
                break

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            self.text.append(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check tutorial figures, required text, resources, and gates."
    )
    parser.add_argument(
        "html",
        nargs="?",
        type=Path,
        default=Path("daphnia_tut_standalone.html"),
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="require zero local page-resource references",
    )
    parser.add_argument(
        "--allow-failed-gates",
        action="store_true",
        help=(
            "permit failed numerical gates after explicit scientific review; "
            "structural checks remain strict"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    parser = TutorialParser()
    parser.feed(args.html.read_text(encoding="utf-8"))
    rendered_text = " ".join(parser.text)

    structural_failures: list[str] = []
    empty_figures = sorted(
        figure_id
        for figure_id, image_count in parser.figure_images.items()
        if image_count == 0
    )
    if empty_figures:
        structural_failures.append(
            "empty numbered figures: " + ", ".join(empty_figures)
        )
    for required in REQUIRED_TEXT:
        if required not in rendered_text:
            structural_failures.append(f"required text missing: {required!r}")
    if args.standalone and parser.local_resources:
        resources = ", ".join(
            f"{tag}:{value}" for tag, value in parser.local_resources
        )
        structural_failures.append(f"local resources remain: {resources}")

    failed_gates = []
    for text_block in parser.text:
        for line in text_block.splitlines():
            match = re.match(
                r"^\s*(.+?(?:gate|validation))\s*:\s*FAIL\s*$",
                line,
                flags=re.IGNORECASE,
            )
            if match:
                failed_gates.append(f"{match.group(1).strip()}: FAIL")
    failed_gates = sorted(set(failed_gates))

    print(f"HTML: {args.html}")
    print(f"Numbered figures: {len(parser.figure_images)}")
    print(f"Empty numbered figures: {len(empty_figures)}")
    print(f"Local page resources: {len(parser.local_resources)}")
    if structural_failures:
        for failure in structural_failures:
            print(f"STRUCTURAL FAIL: {failure}")
    else:
        print("Structural validation: PASS")

    if failed_gates:
        for gate in failed_gates:
            print(f"NUMERICAL FAIL: {gate}")
        if args.allow_failed_gates:
            print(
                "Numerical gate failures explicitly allowed; confirm that "
                "their figures and inferential claims are omitted."
            )
        else:
            print(
                "Numerical validation: FAIL. Do not describe this render as "
                "a manuscript reproduction."
            )
    else:
        print("Numerical validation: PASS")

    if structural_failures:
        return 1
    if failed_gates and not args.allow_failed_gates:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
