from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
import shutil

@dataclass(frozen=True)
class ToolItem:
    name: str
    url: str
    description: str
    category: str
    tags: Tuple[str, ...]


def _slugify_dirname(s: str) -> str:
    """
    Make a stable, filesystem-safe directory name.
    - Keep ASCII alnum, dash, underscore.
    - Convert spaces to '-'
    - For other chars (incl. CJK), keep them (modern filesystems support it),
      but remove path separators and control chars.
    """
    s = (s or "").strip()
    if not s:
        return "untitled"
    s = s.replace("\\", " ").replace("/", " ").replace(":", " ").strip()
    s = " ".join(s.split())
    s = s.replace(" ", "-")
    return s


def _md_escape(s: str) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def _group_tools_by_category(items: List[ToolItem]) -> Dict[str, List[ToolItem]]:
    groups: Dict[str, List[ToolItem]] = {}
    for it in items:
        cat = (it.category or "").strip() or "未分类"
        groups.setdefault(cat, []).append(it)
    # stable ordering
    for cat in groups:
        groups[cat].sort(key=lambda x: (x.name.lower(), x.url.lower()))
    return dict(sorted(groups.items(), key=lambda kv: kv[0]))


def _render_tool_md(category: str, items: List[ToolItem]) -> str:
    lines: List[str] = []
    lines.append(f"# {category}")
    lines.append("")
    lines.append(f"共 {len(items)} 个工具。")
    lines.append("")
    for it in items:
        lines.append(f"## {it.name}")
        lines.append("")
        if it.url:
            lines.append(f"- 链接：<{it.url}>")
        if it.tags:
            lines.append(f"- 关键字：{', '.join(it.tags)}")
        if it.description:
            lines.append("")
            lines.append(_md_escape(it.description))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_tools_index_md(categories: List[str]) -> str:
    lines: List[str] = []
    lines.append("# 解题工具")
    lines.append("")
    lines.append("按分类整理的工具与资料链接。")
    lines.append("")
    lines.append("致谢：https://docs.qq.com/sheet/DR2xTZ293QkhRU0Jo?tab=BB08J2")
    lines.append("")
    lines.append("## 分类")
    lines.append("")
    for cat in categories:
        slug = _slugify_dirname(cat)
        lines.append(f"- [{cat}](./{slug}/index.md)")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_nav_yml(categories: List[str]) -> str:
    """
    Nav structure (YAML):

    - Tools:
      - index: tools/index.md
      - 分类A: tools/分类A/index.md
      - 分类B: tools/分类B/index.md

    You can adapt the top-level title if your project uses another label.
    """
    lines: List[str] = []
    lines.append("- 解题工具:")
    lines.append("  - index: tools/index.md")
    for cat in categories:
        slug = _slugify_dirname(cat)
        lines.append(f"  - {cat}: tools/{slug}/index.md")
    return "\n".join(lines).rstrip() + "\n"


def _coerce_tool_items(tools_data: Any) -> List[ToolItem]:
    """
    Accepts a list of dicts like:
      {name,url,description,category,tags}
    tags can be list/tuple/str/None.
    """
    if tools_data is None:
        return []
    if not isinstance(tools_data, list):
        raise TypeError("tools_data must be a list of dicts")

    items: List[ToolItem] = []
    for i, row in enumerate(tools_data):
        if not isinstance(row, dict):
            raise TypeError(f"tools_data[{i}] must be a dict")

        name = str(row.get("name", "")).strip()
        url = str(row.get("url", "")).strip()
        description = str(row.get("description", "") or "").strip()
        category = str(row.get("category", "") or "").strip()

        tags_raw = row.get("tags", [])
        tags: Tuple[str, ...]
        if tags_raw is None:
            tags = tuple()
        elif isinstance(tags_raw, str):
            t = tags_raw.strip()
            tags = (t,) if t else tuple()
        elif isinstance(tags_raw, (list, tuple)):
            cleaned = []
            for t in tags_raw:
                t2 = str(t).strip()
                if t2:
                    cleaned.append(t2)
            tags = tuple(cleaned)
        else:
            raise TypeError(f"tools_data[{i}].tags must be list/tuple/str/None")

        if not name:
            # allow unnamed? usually useless; skip silently
            continue

        items.append(
            ToolItem(
                name=name,
                url=url,
                description=description,
                category=category,
                tags=tags,
            )
        )
    return items


def generate_tools(
    tools_data: Any,
    *,
    docs_dir: str | Path = "docs",
    nav_output_path: str | Path | None = None,
) -> Dict[str, Any]:
    """
    Generate docs/tools/ folder structure and markdown pages for tools,
    plus a nav.yml snippet (or file) for inclusion in the site navigation.

    Creates:
      docs/tools/index.md
      docs/tools/<category>/index.md   (one per category)

    Parameters
    ----------
    tools_data:
        List[dict] with keys: name, url, description, category, tags.
    docs_dir:
        Root docs directory. Default "docs".
    nav_output_path:
        If provided, write nav YAML to this file path.
        If None, return the nav YAML string in result["nav_yml"].

    Returns
    -------
    dict with keys:
      - written_files: List[str] of relative paths written
      - nav_yml: str (only if nav_output_path is None)
      - categories: List[str]
      - counts: {total:int, by_category: {category:int}}
    """
    docs_dir = Path(docs_dir)
    tools_root = docs_dir / "tools"
    shutil.rmtree(tools_root, ignore_errors=True)
    tools_root.mkdir(parents=True, exist_ok=True)

    items = _coerce_tool_items(tools_data)
    groups = _group_tools_by_category(items)
    categories = list(groups.keys())

    written: List[str] = []

    # index.md
    index_md = _render_tools_index_md(categories)
    (tools_root / "index.md").write_text(index_md, encoding="utf-8")
    written.append(str(Path("tools") / "index.md"))

    # category pages
    for cat, cat_items in groups.items():
        slug = _slugify_dirname(cat)
        cat_dir = tools_root / slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        md = _render_tool_md(cat, cat_items)
        (cat_dir / "index.md").write_text(md, encoding="utf-8")
        written.append(str(Path("tools") / slug / "index.md"))

    nav_yml = _render_nav_yml(categories)
    if nav_output_path is not None:
        nav_output_path = Path(nav_output_path)
        nav_output_path.parent.mkdir(parents=True, exist_ok=True)
        nav_output_path.write_text(nav_yml, encoding="utf-8")
        result_nav = None
    else:
        result_nav = nav_yml

    counts_by_category = {cat: len(groups[cat]) for cat in categories}
    result: Dict[str, Any] = {
        "written_files": written,
        "categories": categories,
        "counts": {"total": len(items), "by_category": counts_by_category},
    }
    if result_nav is not None:
        result["nav_yml"] = result_nav
    return result

if __name__ == "__main__":
    import yaml

    with open("resource/tools.yml", "r", encoding="utf-8") as f:
        tools = yaml.safe_load(f)

    nav_yml = generate_tools(tools, docs_dir="docs", nav_output_path="nav-tools.yml")
