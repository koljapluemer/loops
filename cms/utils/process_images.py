# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow", "numpy", "scikit-image"]
# ///
"""Image pipeline: binarizes data/img_in/* into black-ink-on-transparent webp in data/loops/img/.

Ink is found with a Sauvola threshold on a 4× upscaled grayscale copy; the mask is downsampled
back with antialiasing, trimmed to its content and given a uniform transparent border.
Only inputs newer than their output are processed; --force regenerates everything.
Usage: uv run utils/process_images.py [--force]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from skimage.filters import gaussian, threshold_sauvola

ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = ROOT / "data" / "img_in"
OUTPUT_DIR = ROOT / "data" / "loops" / "img"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
BORDER_PX = 15
UPSCALE = 4


def binarize(img: Image.Image) -> Image.Image:
    """Returns black ink on transparent RGBA, trimmed and padded."""
    img = img.convert("L")
    w, h = img.size

    # Threshold at higher resolution so the downsampled mask gets smooth, antialiased edges
    big = img.resize((w * UPSCALE, h * UPSCALE), Image.Resampling.LANCZOS)
    a = gaussian(np.asarray(big, dtype=np.float32) / 255.0, sigma=0.8)
    threshold = threshold_sauvola(a, window_size=201, k=0.4)
    ink = ((a <= threshold) * 255).astype(np.uint8)

    alpha = Image.fromarray(ink).resize((w, h), Image.Resampling.LANCZOS)

    # Pure black ink, transparent background
    out = Image.new("RGBA", alpha.size, (0, 0, 0, 0))
    out.putalpha(alpha)
    return trim_and_pad(out)


def trim_and_pad(img: Image.Image) -> Image.Image:
    """Crops surrounding transparency, then sets unified padding."""
    img = img.convert("RGBA")
    bbox = img.getchannel("A").getbbox()
    if bbox:
        img = img.crop(bbox)
    return ImageOps.expand(img, border=BORDER_PX, fill=(0, 0, 0, 0))


def process(src: Path, dst: Path) -> None:
    binarize(Image.open(src)).save(dst, "WEBP", lossless=True)


def main() -> None:
    force = "--force" in sys.argv[1:]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for src in sorted(INPUT_DIR.iterdir()):
        if src.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        dst = OUTPUT_DIR / f"{src.stem}.webp"
        if not force and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            print(f"skip {src.name} (up to date)")
            continue
        print(f"{src.name} -> {dst.relative_to(ROOT)}")
        process(src, dst)


if __name__ == "__main__":
    main()
