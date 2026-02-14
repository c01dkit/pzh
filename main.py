from dataclasses import dataclass
from pathlib import Path
import yaml
import shutil
import logging
import datetime
import re 
logging.basicConfig(level=logging.INFO)
logger = logging.Logger("main")

@dataclass(frozen=True)
class ToolItem:
    name: str
    url: str
    description: str
    category: list[str]
    tags: list[str]

@dataclass(frozen=True)
class EventItem:
    name: str
    url: str
    description: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    year: int
    host: str
    tags: list[str]

def slugify_dirname(s: str) -> str:
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

def slugify_event_name(text: str) -> str:
    t = text.strip().lower()
    t = t.replace("&", " and ")
    t = re.sub(r"[\s_]+", "-", t)
    t = re.sub(r"[^a-z0-9\-]+", "", t)
    t = re.sub(r"-{2,}", "-", t).strip("-")
    if not t:
        code = "".join(f"{ord(c):x}" for c in text)[:12]
        t = f"event-{code}"
    return t

def create_event_items(data:list) -> list[EventItem]:
    result = []
    for item in data:
        if item.get('name', '') == '':
            logger.warning("EventItem with missing name found")
            continue
        
        result.append(
            EventItem(
                name=item.get('name'),
                url = item.get('url'),
                description=item.get('description'),
                start_time=item.get('start_time'),
                end_time=item.get('end_time'),
                year=item.get('year'),
                host=item.get('host'),
                tags=item.get('tags', [])
            )
        )
    return result

def create_tool_items(data:list) -> list[ToolItem]:
    result = []
    for item in data:
        if item.get('name', '') == '':
            logger.warning("Item with missing name found")
            continue
        category = item.get('category', '')
        if category == '':
            category = '其他'
        if isinstance(category, str):
            category = [category]
        result.append(
            ToolItem(
                name=item.get('name'),
                url = item.get('url'),
                description=item.get('description'),
                category=category,
                tags=item.get('tags', [])
            )
        )
    return result

def create_tool_groups(tool_items:list[ToolItem]) -> dict[str, list[ToolItem]]:
    result = {}
    for tool in tool_items:
        for cate in tool.category:
            result.setdefault(cate, []).append(tool)
    for cate in result:
        result[cate].sort(key=lambda x: x.name.lower())
    return dict(sorted(result.items(), key=lambda x: x[0].lower()))
def create_event_groups(event_items:list[EventItem]) -> dict[str, list[EventItem]]:
    result = {}
    for event in event_items:
        result.setdefault(event.year, []).append(event)
    for k in result:
        result[k].sort(key=lambda x: (x.start_time or datetime.datetime.min, x.name.lower()))
    return dict(sorted(result.items(), key=lambda x: x[0], reverse=True))

def render_events_index_md(categories: list[str]) -> str:
    lines: list[str] = []
    lines.append("# 赛事总览")
    lines.append("")
    lines.append("按年份整理的赛事链接。")
    lines.append("")
    lines.append("## 年份")
    lines.append("")
    for cat in categories:
        slug = slugify_dirname(str(cat))
        lines.append(f"- [{cat}](./{slug}/index.md)")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def render_tools_index_md(categories: list[str]) -> str:
    lines: list[str] = []
    lines.append("# 解题工具")
    lines.append("")
    lines.append("按分类整理的工具与资料链接。")
    lines.append("")
    lines.append("致谢：https://docs.qq.com/sheet/DR2xTZ293QkhRU0Jo?tab=BB08J2")
    lines.append("")
    lines.append("## 分类")
    lines.append("")
    for cat in categories:
        slug = slugify_dirname(cat)
        lines.append(f"- [{cat}](./{slug}/index.md)")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def md_escape(s: str) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()

def render_event_md(year: str, items: list[EventItem]) -> str:
    lines: list[str] = []
    lines.append(f"# {year} 年赛事")
    lines.append("")
    for e in items:
        name = e.name
        start_time = e.start_time.strftime("%Y-%m-%d %H:%M")
        end_time = e.end_time.strftime("%Y-%m-%d %H:%M")
        host = e.host or ""

        lines.append(f"## {name}")
        lines.append("")

        time_line = ""
        if start_time and end_time:
            time_line = f"- 时间：{start_time} ～ {end_time}"
        elif start_time:
            time_line = f"- 时间：{start_time}"
        if host:
            if time_line:
                time_line += f"  \n- 主办方：{host}"
            else:
                time_line = f"- 主办方：{host}"

        if e.description:
            lines.append(md_escape(e.description))
            lines.append("")

        if time_line:
            lines.append(time_line)
            lines.append("")

        link_parts = [f"[本站](/events/{e.year}/{slugify_event_name(e.name)}/)"]
        link_parts.append(f"[官网]({e.url})")
        lines.append(" · ".join(link_parts))
        lines.append("")  # blank line between events

    return "\n".join(lines).rstrip() + "\n"

def render_tool_md(category: str, items: list[ToolItem]) -> str:
    lines: list[str] = []
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
            lines.append(md_escape(it.description))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_tools(tools_data:list, target_tools_dir:Path) -> str:
    """在指定目录中生成以category进行分组的工具子文件夹，返回对应需要填写在nav里的str
    """
    shutil.rmtree(target_tools_dir, ignore_errors=True)
    target_tools_dir.mkdir(parents=True, exist_ok=True)

    tool_items = create_tool_items(tools_data)
    tool_groups = create_tool_groups(tool_items)

    written = "  - 解题工具:\n"
    # 创建分类下的index
    index_md_content = render_tools_index_md(list(tool_groups.keys()))
    (target_tools_dir / "index.md").write_text(index_md_content, encoding="utf8")
    written += "    - index: tools/index.md\n"
    # 创建分类内的page
    for cate, cate_items in tool_groups.items():
        slug = slugify_dirname(cate)
        cate_dir = target_tools_dir / slug
        cate_dir.mkdir(parents=True, exist_ok=True)
        markdown = render_tool_md(cate, cate_items)
        (cate_dir / "index.md").write_text(markdown, encoding="utf8")
        written += f"    - {slug}: tools/{slug}/index.md\n"
    
    return written
def generate_events(events_data:list, target_events_dir:Path) -> str:
    """在指定目录中生成以年份进行分组的赛事子文件夹，返回对应需要填写在nav里的str
    """
    shutil.rmtree(target_events_dir, ignore_errors=True)
    target_events_dir.mkdir(parents=True, exist_ok=True)
    event_items = create_event_items(events_data)
    event_groups = create_event_groups(event_items)

    written = "  - 赛事总览:\n"
    # 创建分类下的index
    index_md_content = render_events_index_md(list(event_groups.keys()))
    (target_events_dir / "index.md").write_text(index_md_content, encoding="utf8")
    written += "    - index: events/index.md\n"
    # 创建分类内的page
    for cate, cate_items in event_groups.items():
        cate_dir = target_events_dir / str(cate)
        cate_dir.mkdir(parents=True, exist_ok=True)
        markdown = render_event_md(cate, cate_items)
        (cate_dir / "index.md").write_text(markdown, encoding="utf8")
        written += f"    - {cate}:\n"
        written += f"      - index: events/{cate}/index.md\n"
        for e in cate_items:
            slug = slugify_event_name(e.name)
            written += f"      - \"{e.name}\": events/{cate}/{slug}.md\n"
            (cate_dir / f"{slug}.md").write_text(render_event_md(cate, [e]), encoding="utf8")
    return written

if __name__ == "__main__":
    with open("resource/tools.yml", "r", encoding="utf8") as file:
        tools = yaml.safe_load(file)
    
    nav_yml_tools = generate_tools(
        tools,
        Path("docs/tools")
    )


    with open("resource/events.yml", "r", encoding="utf8") as file:
        events = yaml.safe_load(file)

    nav_yml_events = generate_events(
        events, 
        Path("docs/events")
    )

    web_settings = ""
    with open("mkdocs.yml", "r", encoding="utf8") as file:
        reach_mark = False
        for line in file:
            if not reach_mark and "# END NAV" in line:
                reach_mark = True
            if reach_mark:
                web_settings += line

    with open("mkdocs.yml", "w", encoding="utf8") as file:
        file.write("""nav:
  - 首页: 
    - index: index.md
    - 赛事总览: events/index.md
#    - 题目总览: puzzles/index.md
    - 解题工具: tools/index.md
    - 密码表: graphs/index.md
""")
        file.write(nav_yml_events)
        file.write(nav_yml_tools)
        file.write("""  - 密码表:
    - index: graphs/index.md
""")
        file.write(web_settings)
        