# cms

Run everything from `cms/`. Dependencies are managed with `uv`.

```sh
uv sync
```

## Local CMS

```sh
uv run flask --app app run --debug
```

Open http://127.0.0.1:5000. Reads and writes `data/` directly.

Editor keys: `b` erase brush, `c` crop, `[` / `]` brush size, `ctrl+z` undo.

Image edits apply to the processed webp. `utils/process_images.py --force`, or a newer original in `data/img_in/`, regenerates the webp and drops them.

## Static site

```sh
uv run ssg.py
```

Builds into `_site/`.

## Utils

```sh
uv run utils/process_images.py [--force]   # data/img_in/* -> data/loops/img/*.webp
uv run utils/create_loop_data.py           # add missing data/loops/data/<slug>.json
```
