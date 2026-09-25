"""Creates missing loop data files: for every image in data/img_in/ and data/loops/img/
without a matching data/loops/data/<stem>.json, copies data/templates/loop.json there.

Existing json files are never overwritten.
Usage: uv run utils/create_loop_data.py
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DIRS = [ROOT / "data" / "img_in", ROOT / "data" / "loops" / "img"]
DATA_DIR = ROOT / "data" / "loops" / "data"
TEMPLATE = ROOT / "data" / "templates" / "loop.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stems = {
        src.stem
        for image_dir in IMAGE_DIRS
        if image_dir.is_dir()
        for src in image_dir.iterdir()
        if src.suffix.lower() in IMAGE_SUFFIXES
    }
    for stem in sorted(stems):
        dst = DATA_DIR / f"{stem}.json"
        if dst.exists():
            print(f"skip {dst.name} (exists)")
            continue
        print(f"{TEMPLATE.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
        shutil.copyfile(TEMPLATE, dst)


if __name__ == "__main__":
    main()
