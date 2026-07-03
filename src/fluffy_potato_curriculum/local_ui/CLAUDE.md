# local_ui/

A small **local, read-only** FastAPI server for browsing and reviewing the generated
lesson materials in a browser instead of opening files one at a time. This is a
developer/reviewer tool — it is *not* student-facing course code and is not imported by
any lesson.

## Run it

```sh
uv run python -m fluffy_potato_curriculum.local_ui   # serves http://127.0.0.1:8000/
```

`HOST` / `PORT` env vars override the bind address.

## Shape

```
catalog.py   # reads lessons/tracks.toml (source of truth) + scans L<NN>/ dirs into typed items
models.py    # Pydantic payloads: Track, LessonSummary, LessonDetail, LessonItem, RenderedItem
render.py    # .md -> HTML (markdown lib); .ipynb -> HTML fragment, walked cell by cell
app.py       # FastAPI: create_app(lessons_dir) -> JSON API + serves static/
__main__.py  # uvicorn entrypoint
static/      # dependency-free vanilla-JS single page (index.html, app.js, style.css)
```

The frontend is a **JSON API + JS frontend**: the backend renders `.md`/`.ipynb` to HTML
fragments server-side and returns them inside the JSON payload; `static/app.js` fetches and
injects them. No JS build step.

## Conventions worth knowing

- **`tracks.toml` is the source of truth** for track membership, order, and titles — the
  catalog layers a filesystem scan on top to discover the item files. Don't hardcode the
  lesson list here.
- **`create_app(lessons_dir=...)`** takes the lessons root as a parameter so tests point it
  at a temp tree (`tests/local_ui/conftest.py` builds a fake one). Prefer that over patching.
- **Path-traversal safety:** item content is resolved through `catalog.find_item`, which
  looks the client-supplied `item_id` up in the catalog and only reads a file we already
  discovered — never a raw path join. Keep it that way.
- **Notebook rendering is intentionally hand-rolled** (not nbconvert) so the output is a
  small, controllable fragment with no `<html>` wrapper or surprise CSS. Rendered notebook
  HTML from cell outputs is treated as *trusted local material* — do not point this at
  untrusted `.ipynb` files.
- Deps: `fastapi`, `uvicorn`, `markdown`, `pygments` (runtime); `types-Markdown` (dev). Added
  via `uv add`, so they're in `uv.lock`.
- **Syntax highlighting is server-side via Pygments.** Markdown fences go through the
  `codehilite` extension; notebook code cells (always Python) are highlighted directly. Both
  emit a `.highlight` wrapper so one block of token CSS in `static/style.css` styles both. The
  token CSS is generated from Pygments' `one-dark` style (the viewer chrome is a dark theme) —
  regenerate with `HtmlFormatter(style=...).get_style_defs("#item-html .highlight")` if you
  change it.
- Tests live in `tests/local_ui/` and use FastAPI's `TestClient` fully offline. Its
  httpx-backed methods read as partially-typed under pyright strict, so the calls are
  isolated behind `tests/local_ui/_api.py`.
