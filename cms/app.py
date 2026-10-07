"""Local CMS: create, edit and delete loops directly in data/loops/.

Usage: uv run flask --app app run --debug
"""

import json
import re
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_file, url_for
from PIL import Image

from utils.process_images import binarize, trim_and_pad

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "loops"
IMG_DIR = DATA_DIR / "img"
META_DIR = DATA_DIR / "data"
IMG_IN_DIR = ROOT / "data" / "img_in"
TEMPLATE = ROOT / "data" / "templates" / "loop.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
SLUG_RE = re.compile(r"^[a-z0-9-]+$")

app = Flask(__name__, template_folder="app_templates")
app.secret_key = "local-only"


def check_slug(slug: str) -> str:
    if not SLUG_RE.match(slug):
        abort(400, "invalid slug")
    return slug


def img_path(slug: str) -> Path:
    return IMG_DIR / f"{slug}.webp"


def meta_path(slug: str) -> Path:
    return META_DIR / f"{slug}.json"


def read_meta(slug: str) -> dict:
    return json.loads(meta_path(slug).read_text())


def write_meta(slug: str, data: dict) -> None:
    meta_path(slug).write_text(json.dumps(data, indent=4, ensure_ascii=False))


def load_loop(slug: str) -> dict:
    img = img_path(slug)
    if not img.exists() or not meta_path(slug).exists():
        abort(404)
    return {"slug": slug, "meta": read_meta(slug), "v": int(img.stat().st_mtime)}


@app.get("/")
def index():
    loops = [load_loop(img.stem) for img in sorted(IMG_DIR.glob("*.webp"))]
    return render_template("index.html", loops=loops)


@app.post("/new")
def new():
    file = request.files.get("file")
    display_name = request.form.get("displayName", "").strip()
    slug = request.form.get("slug", "").strip()
    suffix = Path(file.filename).suffix.lower() if file and file.filename else ""
    error = None
    if not SLUG_RE.match(slug):
        error = "invalid slug"
    elif img_path(slug).exists() or meta_path(slug).exists():
        error = f"slug '{slug}' exists"
    elif suffix not in IMAGE_SUFFIXES:
        error = f"unsupported file type '{suffix}'"
    if error:
        flash(error, "error")
        return redirect(url_for("index"))

    IMG_IN_DIR.mkdir(parents=True, exist_ok=True)
    src = IMG_IN_DIR / f"{slug}{suffix}"
    file.save(src)
    binarize(Image.open(src)).save(img_path(slug), "WEBP", lossless=True)

    data = json.loads(TEMPLATE.read_text())
    data["displayName"] = display_name
    write_meta(slug, data)
    return redirect(url_for("edit", slug=slug))


@app.get("/loop/<slug>")
def edit(slug):
    return render_template("edit.html", loop=load_loop(check_slug(slug)))


@app.post("/loop/<slug>/meta")
def update_meta(slug):
    load_loop(check_slug(slug))
    data = read_meta(slug)
    data["displayName"] = request.form.get("displayName", "").strip()
    write_meta(slug, data)
    flash("saved", "success")
    return redirect(url_for("edit", slug=slug))


@app.post("/loop/<slug>/image")
def update_image(slug):
    load_loop(check_slug(slug))
    img = Image.open(request.files["image"].stream)
    trim_and_pad(img).save(img_path(slug), "WEBP", lossless=True)
    return "", 204


@app.post("/loop/<slug>/delete")
def delete(slug):
    check_slug(slug)
    img_path(slug).unlink(missing_ok=True)
    meta_path(slug).unlink(missing_ok=True)
    for src in IMG_IN_DIR.glob(f"{slug}.*"):
        if src.stem == slug:
            src.unlink()
    flash(f"deleted {slug}", "success")
    return redirect(url_for("index"))


@app.get("/img/<slug>")
def image(slug):
    img = img_path(check_slug(slug))
    if not img.exists():
        abort(404)
    return send_file(img, mimetype="image/webp", max_age=0)
