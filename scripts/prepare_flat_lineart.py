#!/usr/bin/env python3
"""Prepare clean binary line art from a light-background flat illustration.

This intentionally selects existing dark ink instead of detecting edges.  It is
for white/light backgrounds with dark outlines and flat color fills, not photos.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract existing dark ink from a flat illustration."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int)
    parser.add_argument("--min-threshold", type=int, default=45)
    parser.add_argument("--max-threshold", type=int, default=85)
    parser.add_argument("--max-foreground", type=float, default=0.055)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def composite_rgb(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        return Image.alpha_composite(background, rgba).convert("RGB")
    return image.convert("RGB")


def main() -> int:
    args = parse_args()
    if not 0 <= args.min_threshold <= args.max_threshold <= 255:
        raise SystemExit("thresholds must satisfy 0 <= min <= max <= 255")
    if not 0 < args.max_foreground < 1:
        raise SystemExit("--max-foreground must be between 0 and 1")

    with Image.open(args.input) as opened:
        image = composite_rgb(opened)

    height = args.height or round(image.height * args.width / image.width)
    width = args.width
    width += width % 2
    height += height % 2
    gray = image.resize((width, height), Image.Resampling.LANCZOS).convert("L")
    histogram = gray.histogram()
    total = width * height

    selected = None
    selected_ratio = None
    cumulative = 0
    ratios: dict[int, float] = {}
    for value, count in enumerate(histogram):
        cumulative += count
        if args.min_threshold <= value <= args.max_threshold:
            ratios[value] = cumulative / total

    for threshold in range(args.min_threshold, args.max_threshold + 1):
        ratio = ratios[threshold]
        if ratio <= args.max_foreground:
            selected = threshold
            selected_ratio = ratio

    if selected is None or selected_ratio is None:
        ratio = ratios[args.min_threshold]
        raise SystemExit(
            "source is too dense for flat-illustration ink extraction: "
            f"foreground ratio {ratio:.4f} already exceeds {args.max_foreground:.4f} "
            f"at threshold {args.min_threshold}; use a neural line-art provider"
        )

    binary = gray.point(lambda value: 0 if value <= selected else 255, mode="1")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    binary.save(args.output)

    report = {
        "source": str(args.input),
        "output": str(args.output),
        "width": width,
        "height": height,
        "threshold": selected,
        "foreground_ratio": round(selected_ratio, 6),
        "max_foreground": args.max_foreground,
        "method": "dark-ink-selection",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
