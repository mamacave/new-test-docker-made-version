"""Compare two screenshots and exit non-zero if difference exceeds threshold.

Usage:
    python scripts/ci/compare_screenshots.py baseline.png current.png --threshold 0.01

Threshold is fraction of non-empty pixels (0.01 = 1%).
"""

import sys
from PIL import Image, ImageChops


def compare(baseline_path, current_path, threshold=0.01, output_path=None):
    b = Image.open(baseline_path).convert("RGBA")
    c = Image.open(current_path).convert("RGBA")
    if b.size != c.size:
        print(f"Size mismatch: baseline={b.size} current={c.size}")
        return 2

    diff = ImageChops.difference(b, c)
    bbox = diff.getbbox()
    if not bbox:
        print("Images identical")
        return 0

    # Count non-zero pixels in the diff
    non_zero = 0
    total = b.size[0] * b.size[1]
    for px in diff.getdata():
        # px is an (r,g,b,a) tuple
        if px[0] or px[1] or px[2] or px[3]:
            non_zero += 1

    frac = non_zero / total
    print(f"Non-matching pixel fraction: {frac:.6f}")

    # Optionally write a visual diff image
    if output_path:
        # create a red-highlighted diff overlay
        overlay = Image.new("RGBA", b.size, (255, 0, 0, 120))
        mask = diff.convert("L").point(lambda p: 255 if p else 0)
        out = b.convert("RGBA")
        out.paste(overlay, (0, 0), mask)
        out.save(output_path)
        print(f"Wrote visual diff to {output_path}")

    if frac > threshold:
        print(f"Above threshold ({threshold}); failing")
        return 1
    print(f"Below threshold ({threshold}); passing")
    return 0


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("baseline")
    p.add_argument("current")
    p.add_argument("--threshold", type=float, default=0.01)
    p.add_argument("--output", type=str, default=None)
    args = p.parse_args()

    sys.exit(compare(args.baseline, args.current, args.threshold, args.output))
