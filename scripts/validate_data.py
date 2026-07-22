#!/usr/bin/env python3
"""Validate every JSON file under data/ against schema/data-entry.schema.json.

Usage: python3 scripts/validate_data.py
Exits 0 if all files conform, 1 otherwise.
"""
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("error: this script requires the 'jsonschema' package (pip install jsonschema)")

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SCHEMA_PATH = REPO_ROOT / "schema" / "data-entry.schema.json"


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = Draft202012Validator(schema)

    json_files = sorted(DATA_DIR.rglob("*.json"))
    if not json_files:
        print(f"no JSON files found under {DATA_DIR}")
        return 0

    had_errors = False
    for path in json_files:
        rel_path = path.relative_to(REPO_ROOT)
        try:
            instance = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            had_errors = True
            print(f"{rel_path}: invalid JSON ({e})")
            continue

        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            had_errors = True
            for error in errors:
                pointer = "/".join(str(p) for p in error.path) or "(root)"
                print(f"{rel_path}: [{pointer}] {error.message}")

    if had_errors:
        return 1

    print(f"all {len(json_files)} files conform to schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
