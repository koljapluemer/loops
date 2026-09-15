"""Static site generator: renders data/loops/* into _site/."""

import json
import shutil
import subprocess
from pathlib import Path

import jinja2

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data" / "loops"
TEMPLATES_DIR = ROOT / "cms" / "templates"
OUTPUT_DIR = ROOT / "_site"

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(["jinja", "html"]),
)


def load_loops() -> list[dict]:
    loops = []
    for loop_dir in sorted(DATA_DIR.iterdir()):
        if not loop_dir.is_dir():
            continue
        data = json.loads((loop_dir / "data.json").read_text())
        loops.append({"slug": loop_dir.name, "title": data["title"]})
    return loops


def render_diagram(loop_dir: Path, out_svg: Path) -> str:
    subprocess.run(
        ["d2", "--layout", "elk", str(loop_dir / "loop.d2"), str(out_svg)],
        check=True,
    )
    return out_svg.read_text()


def build() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    shutil.copy(TEMPLATES_DIR / "styles.css", OUTPUT_DIR / "styles.css")

    loops = load_loops()

    index_template = env.get_template("index.jinja")
    (OUTPUT_DIR / "index.html").write_text(index_template.render(loops=loops))

    loop_template = env.get_template("loop.jinja")
    for loop in loops:
        loop_dir = DATA_DIR / loop["slug"]
        out_dir = OUTPUT_DIR / "loops" / loop["slug"]
        out_dir.mkdir(parents=True)
        svg = render_diagram(loop_dir, out_dir / "loop.svg")
        (out_dir / "index.html").write_text(
            loop_template.render(title=loop["title"], svg=svg)
        )


if __name__ == "__main__":
    build()
