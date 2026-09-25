"""Image pipeline: removes backgrounds from data/img_in/* and writes trimmed grayscale webp to data/loops/img/.

Requires `magick` (ImageMagick 7) on PATH; rembg is run via uvx.
Only inputs newer than their output are processed; --force regenerates everything.
Usage: uv run utils/process_images.py [--force]
"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = ROOT / "data" / "img_in"
OUTPUT_DIR = ROOT / "data" / "loops" / "img"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
BORDER_PX = 15

REMBG = ["uvx", "--from", "rembg[cpu,cli]", "rembg"]


def process(src: Path, dst: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        cutout = Path(tmp) / "cutout.png"
        subprocess.run([*REMBG, "i", str(src), str(cutout)], check=True)
        subprocess.run(
            [
                "magick", str(cutout),
                "-colorspace", "Gray",
                "-trim", "+repage",
                "-bordercolor", "none", "-border", str(BORDER_PX),
                str(dst),
            ],
            check=True,
        )


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
