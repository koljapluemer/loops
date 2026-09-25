"""Static site generator: renders data/loops/{img,data}/* into _site/."""

import json
import shutil
import subprocess
from pathlib import Path

import jinja2

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "loops"
IMG_DIR = DATA_DIR / "img"
META_DIR = DATA_DIR / "data"
TEMPLATES_DIR = ROOT / "cms" / "templates"
OUTPUT_DIR = ROOT / "_site"
# thumbnails live outside _site (which is wiped every build) so they can be reused
THUMB_CACHE_DIR = ROOT / ".cache" / "thumbs"
THUMB_SIZE = "800x600>"

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(["jinja", "html"]),
)


def load_loops() -> list[dict]:
    loops = []
    for img in sorted(IMG_DIR.glob("*.webp")):
        data = json.loads((META_DIR / f"{img.stem}.json").read_text())
        loops.append({"slug": img.stem, "title": data["displayName"], "img": img})
    return loops


def ensure_thumbnail(img: Path) -> Path:
    """Returns a cached thumbnail for img, regenerating it only if img is newer."""
    thumb = THUMB_CACHE_DIR / img.name
    if thumb.exists() and thumb.stat().st_mtime >= img.stat().st_mtime:
        return thumb
    print(f"thumbnail {img.name}")
    THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["magick", str(img), "-thumbnail", THUMB_SIZE, str(thumb)],
        check=True,
    )
    return thumb


def build() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    shutil.copy(TEMPLATES_DIR / "styles.css", OUTPUT_DIR / "styles.css")

    loops = load_loops()

    thumbs_dir = OUTPUT_DIR / "thumbs"
    thumbs_dir.mkdir()
    for loop in loops:
        shutil.copy(ensure_thumbnail(loop["img"]), thumbs_dir / loop["img"].name)
        loop["thumb"] = f"thumbs/{loop['img'].name}"

    index_template = env.get_template("index.jinja")
    (OUTPUT_DIR / "index.html").write_text(index_template.render(loops=loops))

    loop_template = env.get_template("loop.jinja")
    for loop in loops:
        out_dir = OUTPUT_DIR / "loops" / loop["slug"]
        out_dir.mkdir(parents=True)
        shutil.copy(loop["img"], out_dir / "loop.webp")
        (out_dir / "index.html").write_text(
            loop_template.render(title=loop["title"], img="loop.webp")
        )


if __name__ == "__main__":
    build()
