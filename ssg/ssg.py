# build site
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = Path(__file__).parent / "templates"
SITE_DIR = ROOT / "site"


def main():
    shutil.rmtree(SITE_DIR, ignore_errors=True)
    SITE_DIR.mkdir()

    img_src_dir = DATA_DIR / "img"
    img_out_dir = SITE_DIR / "img"

    items = []
    for path in sorted(DATA_DIR.glob("*.json")):
        with path.open() as f:
            item = json.load(f)
        img_path = img_src_dir / f"{path.stem}.webp"
        if img_path.exists():
            img_out_dir.mkdir(exist_ok=True)
            shutil.copy(img_path, img_out_dir / img_path.name)
            item["img"] = f"img/{img_path.name}"
        items.append(item)

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    shutil.copy(TEMPLATES_DIR / "style.css", SITE_DIR / "style.css")

    tmpl = env.get_template("list.html.jinja")
    (SITE_DIR / "index.html").write_text(tmpl.render(items=items))

    print(f"Built {len(items)} items → {SITE_DIR}/index.html")


if __name__ == "__main__":
    main()
