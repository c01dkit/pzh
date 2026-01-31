from __future__ import annotations

import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def generate_events(
    events: List[Dict[str, Any]],
    docs_dir: str | os.PathLike = "docs",
    events_dir: str = "events",
    *,
    overwrite: bool = True,
) -> str:
    """
    Generate mkdocs markdown pages for puzzle hunt events and return nav.yml content.

    - Each event gets its own md file under docs/events/<year>/<slug>.md
    - Each year gets docs/events/<year>/index.md listing events as H3 sections
    - Root index docs/events/index.md links years
    - Returns nav.yml content (string)
    """
    base = Path(docs_dir) / events_dir
    base.mkdir(parents=True, exist_ok=True)

    # ---- helpers ----
    def parse_dt(s: str) -> datetime:
        return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")

    def slugify(text: str) -> str:
        t = text.strip().lower()
        t = t.replace("&", " and ")
        t = re.sub(r"[\s_]+", "-", t)
        t = re.sub(r"[^a-z0-9\-]+", "", t)
        t = re.sub(r"-{2,}", "-", t).strip("-")
        if not t:
            code = "".join(f"{ord(c):x}" for c in text)[:12]
            t = f"event-{code}"
        return t

    def safe_write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            return
        path.write_text(content, encoding="utf-8")

    def md_escape(s: str) -> str:
        return s.replace("\n", " ").strip()

    def normalize_url_https(url: str) -> str:
        u = (url or "").strip()
        if not u:
            return ""
        if u.startswith("https://"):
            return u
        if u.startswith("http://"):
            return "https://" + u[len("http://") :]
        # If user passed protocol-relative like //example.com, force https
        if u.startswith("//"):
            return "https:" + u
        return "https://" + u.lstrip("/")

    def make_event_md(e: Dict[str, Any]) -> str:
        name = str(e.get("name", "")).strip()
        url = str(e.get("url", "")).strip()
        desc = e.get("description", "")
        desc = "" if desc is None else str(desc).strip()
        host = str(e.get("host", "")).strip()
        start_s = str(e.get("start_time", "")).strip()
        end_s = str(e.get("end_time", "")).strip()

        start_dt = parse_dt(start_s) if start_s else None
        end_dt = parse_dt(end_s) if end_s else None

        def fmt_dt(dt: datetime | None) -> str:
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""

        lines: List[str] = []
        lines.append(f"# {md_escape(name)}")
        lines.append("")
        lines.append("## 信息")
        lines.append("")
        lines.append(f"- **URL**: {url}" if url else "- **URL**: ")
        lines.append(f"- **Host**: `{host}`" if host else "- **Host**: ")
        lines.append(f"- **开始时间（中国时间）**: {fmt_dt(start_dt)}")
        lines.append(f"- **结束时间（中国时间）**: {fmt_dt(end_dt)}")
        if desc:
            lines.append("")
            lines.append("## 备注")
            lines.append("")
            lines.append(desc)
        lines.append("")
        return "\n".join(lines)

    def make_year_index_md(year: int, items: List[Tuple[Dict[str, Any], str]]) -> str:
        """
        items: [(event_dict, filename), ...]
        Render each event as:

        ### 名称

        start ~ end `host`

        [本站](./file.md) · [官网](https://...)
        """
        lines: List[str] = [f"# {year}", ""]

        def sort_key(it: Tuple[Dict[str, Any], str]):
            e, _fn = it
            st = str(e.get("start_time", "")).strip()
            try:
                dt = parse_dt(st)
            except Exception:
                dt = datetime.max
            return (dt, str(e.get("name", "")))

        for e, fn in sorted(items, key=sort_key):
            name = str(e.get("name", "")).strip()
            url = str(e.get("url", "")).strip()
            host = str(e.get("host", "")).strip()
            st = str(e.get("start_time", "")).strip()
            ed = str(e.get("end_time", "")).strip()

            site_link = f"./{fn}"
            official = normalize_url_https(url)

            # --- block ---
            lines.append(f"### {md_escape(name)}")
            lines.append("")
            if st and ed:
                time_line = f"{st} ~ {ed}"
            elif st:
                time_line = f"{st}"
            elif ed:
                time_line = f"~ {ed}"
            else:
                time_line = ""

            if host:
                time_line = (time_line + " " if time_line else "") + f"`{host}`"

            if time_line:
                lines.append(time_line)
                lines.append("")

            link_parts = [f"[本站]({site_link})"]
            if official:
                link_parts.append(f"[官网]({official})")
            lines.append(" · ".join(link_parts))
            lines.append("")  # blank line between events

        return "\n".join(lines).rstrip() + "\n"

    def make_root_index_md(years: List[int]) -> str:
        lines = ["# 赛事总览", "", "## 按年份", ""]
        for y in years:
            lines.append(f"- [{y}](./{y}/index.md)")
        lines.append("")
        return "\n".join(lines)

    # ---- normalize + group ----
    normalized: List[Dict[str, Any]] = []
    for e in events:
        if not isinstance(e, dict):
            continue
        if not e.get("name") or not e.get("year"):
            continue

        ee = dict(e)
        ee["year"] = int(ee["year"])
        ee["url"] = normalize_url_https(str(ee.get("url", "")).strip())
        normalized.append(ee)

    by_year: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for e in normalized:
        by_year[int(e["year"])].append(e)

    years = sorted(by_year.keys(), reverse=True)

    # ---- generate event files + year indexes ----
    year_nav_items: Dict[int, List[Tuple[str, str]]] = defaultdict(list)

    for y in years:
        year_dir = base / str(y)
        year_dir.mkdir(parents=True, exist_ok=True)

        used_filenames: set[str] = set()
        year_items_for_index: List[Tuple[Dict[str, Any], str]] = []

        def event_sort_key(e: Dict[str, Any]):
            st = str(e.get("start_time", "")).strip()
            try:
                dt = parse_dt(st)
            except Exception:
                dt = datetime.max
            return (dt, str(e.get("name", "")))

        for e in sorted(by_year[y], key=event_sort_key):
            name = str(e.get("name", "")).strip()
            slug = slugify(name)

            fn = f"{slug}.md"
            i = 2
            while fn in used_filenames:
                fn = f"{slug}-{i}.md"
                i += 1
            used_filenames.add(fn)

            safe_write(year_dir / fn, make_event_md(e))

            year_items_for_index.append((e, fn))
            year_nav_items[y].append((name, f"{events_dir}/{y}/{fn}"))

        safe_write(year_dir / "index.md", make_year_index_md(y, year_items_for_index))

    safe_write(base / "index.md", make_root_index_md(years))

    # ---- nav.yml ----
    nav_lines: List[str] = []
    nav_lines.append("- 赛事总览:")
    nav_lines.append(f"  - {events_dir}/index.md")
    for y in years:
        nav_lines.append(f"  - {y}:")
        nav_lines.append(f"    - {events_dir}/{y}/index.md")
        for name, path in year_nav_items[y]:
            nav_lines.append(f"    - \"{name}\": {path}")

    return "\n".join(nav_lines) + "\n"


if __name__ == "__main__":
    import yaml

    with open("resource/events.yml", "r", encoding="utf-8") as f:
        events = yaml.safe_load(f)

    nav_yml = generate_events(events, docs_dir="docs", events_dir="events", overwrite=True)

    with open("nav-events.yml", "w", encoding="utf-8") as f:
        f.write(nav_yml)