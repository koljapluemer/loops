"""Writes accepted proposals into the git-tracked data/ tree and commits them.

Not part of the public site; run only locally by whoever is reviewing
proposals (see app.py / README.md).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def is_valid_slug_segment(s: str | None) -> bool:
    return isinstance(s, str) and bool(SLUG_RE.match(s))


def existing_tops() -> list[str]:
    return sorted(p.name for p in DATA_DIR.iterdir() if p.is_dir())


def _id_to_path(entry_id: str) -> Path:
    return DATA_DIR.joinpath(*entry_id.split(":")).with_suffix(".json")


def _object_file_path(top: str, sub: str | None, slug: str) -> Path:
    segments = [top, sub, slug] if sub else [top, slug]
    return DATA_DIR.joinpath(*segments).with_suffix(".json")


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")


def _git_add_commit(rel_paths: list[str], message: str) -> None:
    subprocess.run(["git", "add", *rel_paths], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)


def validate_object_proposal(p: dict[str, Any]) -> None:
    if p.get("top") not in existing_tops():
        raise ValueError(f"unknown top-level category: {p.get('top')!r}")
    if p.get("sub") and not is_valid_slug_segment(p["sub"]):
        raise ValueError(f"invalid subcategory: {p.get('sub')!r}")
    if not is_valid_slug_segment(p.get("slug")):
        raise ValueError(f"invalid slug: {p.get('slug')!r}")
    if not p.get("name") or not str(p["name"]).strip():
        raise ValueError("name is required")


def accept_object_proposal(p: dict[str, Any]) -> str:
    """Writes the proposed object as a new JSON file under data/ and commits it.

    Raises if the target path already exists, so proposals never clobber
    existing entries — the reviewer has to resolve the conflict manually.
    """
    validate_object_proposal(p)
    file_path = _object_file_path(p["top"], p.get("sub"), p["slug"])
    if file_path.exists():
        raise ValueError(f"file already exists: {file_path.relative_to(REPO_ROOT)}")

    entry: dict[str, Any] = {"name": [[p["name"].strip()]]}
    if p.get("description"):
        entry["description"] = [[p["description"].strip()]]
    topics = [t.strip() for t in (p.get("topics") or []) if t and t.strip()]
    if topics:
        entry["topics"] = [[t] for t in topics]
    if p.get("url"):
        entry["urls"] = [[p["url"].strip(), (p.get("url_label") or p["url"]).strip()]]

    _write_json(file_path, entry)
    rel_path = str(file_path.relative_to(REPO_ROOT))
    sub_part = f"/{p['sub']}" if p.get("sub") else ""
    _git_add_commit(
        [rel_path],
        f"data: add {p['top']}{sub_part}/{p['slug']}\n\n"
        f"Proposed by {p.get('submitted_by_email', 'unknown')}, accepted via local-cms.",
    )
    return rel_path


def validate_relationship_proposal(p: dict[str, Any]) -> None:
    if not p.get("source_id") or not _id_to_path(p["source_id"]).exists():
        raise ValueError(f"unknown source object: {p.get('source_id')!r}")
    if not p.get("target_id") or not _id_to_path(p["target_id"]).exists():
        raise ValueError(f"unknown target object: {p.get('target_id')!r}")
    if not p.get("context") or not is_valid_slug_segment(slugify(p["context"])):
        raise ValueError(f"invalid context: {p.get('context')!r}")
    if not p.get("label") or not str(p["label"]).strip():
        raise ValueError("relationship description is required")


def accept_relationship_proposal(p: dict[str, Any]) -> str:
    """Adds the proposed rel into the source object's contexts.<context>.rels
    map and commits the change. If a rel to the same target already exists
    in that context, the new label is appended rather than overwriting it.
    """
    validate_relationship_proposal(p)
    file_path = _id_to_path(p["source_id"])
    raw = json.loads(file_path.read_text())

    ctx_key = slugify(p["context"])
    contexts = raw.setdefault("contexts", {})
    context = contexts.setdefault(ctx_key, {"rels": {}})
    rels = context.setdefault("rels", {})
    rels.setdefault(p["target_id"], []).append([p["label"].strip()])

    _write_json(file_path, raw)
    rel_path = str(file_path.relative_to(REPO_ROOT))
    _git_add_commit(
        [rel_path],
        f"data: relate {p['source_id']} -> {p['target_id']} ({ctx_key})\n\n"
        f"Proposed by {p.get('submitted_by_email', 'unknown')}, accepted via local-cms.",
    )
    return rel_path
