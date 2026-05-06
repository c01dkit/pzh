# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Static MkDocs site that catalogues puzzle hunt events, the puzzles in them, and useful solving tools. The repo is dual-purpose: `src/` is a small Python pipeline that generates Markdown into `docs/`, and `docs/` + `mkdocs.yml` + `overrides/` are consumed by `mkdocs-material` to build the public site (deployed via `gh-deploy`).

The `mkdocs-toolchain` git submodule provides TonyCrane's category-menu plugin and other theme bits — `git submodule update --init --recursive` after a fresh clone.

## Common commands

- `uv sync` — install Python deps (Python 3.13, see `.python-version`).
- `uv run src/main.py` — regenerate everything in `docs/` from the YAML source-of-truth and rewrite `mkdocs.yml` nav.
- `uv run mkdocs serve` — local preview at http://127.0.0.1:8000.
- `uv run mkdocs gh-deploy --clean` — build and push to the `gh-pages` branch.
- `./run.sh ["commit msg"]` — full release: regenerate, `git add . && git commit && git push`, then `gh-deploy`.

There are no tests or linters configured.

## Pipeline architecture (src/)

`src/main.py` is the only entry point. It calls three generators (each returns a nav-fragment string) and then rewrites `mkdocs.yml`:

1. `generate_event_docs.main()` — reads `src/resources/events.yml`, groups events by year, writes `docs/events/index.md`, `docs/events/{year}/index.md`, and `docs/events/{year}/{event_id}.md`. Status emoji (🟢🟠🔴) is decided by counting how many puzzles for that event have `ready: true` (see `get_event_status_dict`).
2. `generate_tool_docs.main()` — reads `src/resources/tools.yml`, groups by `category`, writes `docs/tools/{category-slug}/index.md`. Category sort uses a hard-coded priority dict (`必备` first, `工具杂项类` / `其他杂项类` last).
3. `generate_puzzle_docs.main()` — walks every YAML in `src/resources/puzzle-configs/`, materializes per-puzzle directories under `src/resources/puzzles/{id[:2]}/{id}/main.md` from `src/resources/puzzles/template.md`, and (only for `ready: true` puzzles) renders `docs/puzzles/{id}.md` plus appends a section to the corresponding event page.
4. `generate_mkdocs_yml.main(...)` — overwrites `mkdocs.yml` from scratch up to the `# END NAV` sentinel, splicing in the three nav fragments. **Everything above `# END NAV` is regenerated; everything from `# END NAV` onward is preserved verbatim.** Edit theme/plugins/extensions only below that marker.

### IDs are generated and written back

`src/scripts/setup_id.py` assigns 16-char hex IDs (`secrets.token_hex(8)`) to entries that lack them in `events.yml`, `tools.yml`, and every `puzzle-configs/*.yml`, then **rewrites the YAML in place** with `yaml.dump`. This means:
- Editing those YAML files via the pipeline reflows them (loses comments, normalizes formatting). Authors should treat the YAML files as data, not as hand-tuned text.
- Never reuse / hand-author IDs; let `main.py` mint them. The recursion is depth-limited to 1 (top-level list items only).
- `puzzle_item.id[:2]` is the directory shard under `src/resources/puzzles/`, so renaming an ID will orphan a shard.

### Puzzle authoring loop

1. Add a stub entry to a `src/resources/puzzle-configs/*.yml` (one file per event; see README for the schema). Leave `id` blank and `ready: false`.
2. Run `uv run src/main.py`. The script assigns an ID and copies `src/resources/puzzles/template.md` into `src/resources/puzzles/{id[:2]}/{id}/main.md`.
3. Edit that `main.md` to write the solution. Solver code/data files (`main.py`, images) live alongside it and are pulled in via mkdocs `--8<--` snippet syntax (e.g. `--8<-- "src/resources/puzzles/c5/c506b854f213ee82/main.py"`).
4. Flip `ready: true` in the YAML and re-run `main.py` to publish.

**Footgun:** `copy_template` (in `src/scripts/utils.py`) re-copies the template whenever `template.md`'s mtime exceeds the destination's. If you edit `template.md` while puzzles still have `ready: false`, their unfinished `main.md` files will be **overwritten**. Only touch the template when no in-flight puzzles exist.

### Image handling

Authors paste Snipaste screenshots into `main.md` with the default `![alt text](Snipaste_xxxx.png)` form. `replace_img_lines` (utils.py) rewrites those lines at render time to absolute `https://github.com/c01dkit/pzh/blob/main/src/resources/puzzles/{shard}/{id}/...?raw=true` URLs. The image file must be committed to `main` before `mkdocs serve` can resolve it locally.

## Layout

- `src/resources/events.yml`, `tools.yml`, `puzzle-configs/*.yml` — **source of truth**. Edit these.
- `src/resources/puzzles/{shard}/{id}/main.md` — per-puzzle solution write-up (also source of truth, but indexed by ID).
- `docs/` — **generated**, except `docs/index.md`, `docs/CNAME`, `docs/graphs/`, and `docs/assets/`. The three subtrees `docs/events/`, `docs/tools/`, `docs/puzzles/` are wiped (`shutil.rmtree`) and rebuilt on every run; do not hand-edit them.
- `docs/graphs/` and `docs/assets/images/` — manually maintained cipher-table page; new entries go in `docs/graphs/index.md` (the README marks automation here as TODO).
- `mkdocs.yml` — top portion auto-generated above `# END NAV`; theme/plugins/markdown extensions are below.
- `overrides/` — Material theme overrides (`base.html`, `main.html`, `partials/`, `css/`, `js/`).
- `mkdocs-toolchain/` — submodule, do not modify in this repo.
- `src/scripts/local/` — one-off authoring helpers (e.g. `create_puzzle_config.py`, `parse_seco2.py`); not invoked by `main.py`.

## Conventions

- All user-facing strings, commit messages, and log output are in Chinese; match the surrounding tone when editing rendered Markdown or log lines.
- Generators all use `find_project_root()` (walks up looking for `mkdocs.yml`) — keep using it instead of hard-coded paths so scripts stay runnable from any cwd.
- Sort/priority ordering is encoded as small hard-coded dicts inside each generator (see `create_tool_groups`, the puzzle-index `priority` dict). Add new categories there if they need to deviate from alphabetical.
