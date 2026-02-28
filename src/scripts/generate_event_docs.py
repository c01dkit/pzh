import yaml
import shutil
import datetime
import re 
import copy
import subprocess

from pathlib import Path
from .log import get_logger
from .utils import find_project_root, slugify_dirname
from .models import EventItem


def md_escape(s: str) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()

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
                id=item.get('id'),
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

def create_event_groups(event_items:list[EventItem]) -> dict[str, list[EventItem]]:
    result = {}
    for event in event_items:
        result.setdefault(event.year, []).append(event)
        # logger.debug(f"{event.start_time} is {type(event.start_time)}, {event.end_time} is {type(event.end_time)}")
    for k in result:
        result[k].sort(key=lambda x: (x.start_time, x.name.lower()))
    return dict(sorted(result.items(), key=lambda x: x[0], reverse=True))

def render_events_index_md(categories: list[str]) -> str:
    """生成赛事总览中包含各个年份链接的总index"""
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

def render_event_for_one_year_md(year: str, items: list[EventItem]) -> str:
    """生成某年所有赛事的index界面"""
    lines: list[str] = []
    lines.append(f"# {year}年赛事")
    lines.append("")
    for e in items:
        name = e.name
        start_time = e.start_time.strftime("%Y-%m-%d %H:%M") if e.start_time else None
        end_time = e.end_time.strftime("%Y-%m-%d %H:%M") if e.end_time else None
        host = e.host or ""

        lines.append(f"## {name}")
        lines.append("")

        # 比赛时间、主办方、网址
        if start_time and end_time:
            lines.append(f"- 时间：{start_time} ～ {end_time}")
        elif start_time:
            lines.append(f"- 时间：{start_time}")
        if host:
            lines.append(f"- 主办方：{host}")
        if e.url:
            lines.append(f"- 网站链接：[本站](/events/{e.year}/{e.id}/) · [官网]({e.url})")

        if e.description:
            lines.append("")
            lines.append(md_escape(e.description))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def render_single_event_md(year: str, event_item: EventItem) -> str:
    """生成某个具体赛事的界面"""
    lines: list[str] = []
    lines.append(f"# {year}年赛事")
    lines.append("")
    name = event_item.name
    start_time = event_item.start_time.strftime("%Y-%m-%d %H:%M")
    end_time = event_item.end_time.strftime("%Y-%m-%d %H:%M") if isinstance(event_item.end_time, datetime.datetime) else None
    host = event_item.host or ""

    lines.append(f"## {name}")
    lines.append("")

    # 比赛时间、主办方、网址
    if start_time and end_time:
        lines.append(f"- 时间：{start_time} ～ {end_time}")
    elif start_time:
        lines.append(f"- 时间：{start_time}")
    if host:
        lines.append(f"- 主办方：{host}")
    if event_item.url:
        lines.append(f"- 网站链接：[{event_item.url}]({event_item.url})")

    if event_item.description:
        lines.append("")
        lines.append(md_escape(event_item.description))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def generate_events(events_data:list, target_events_dir:Path) -> str:
    """在指定目录中生成以年份进行分组的赛事子文件夹，返回对应需要填写在nav里的str
    """
    shutil.rmtree(target_events_dir, ignore_errors=True)
    target_events_dir.mkdir(parents=True, exist_ok=True)
    event_items = create_event_items(events_data)
    event_groups = create_event_groups(event_items)

    written = "  - 赛事总览:\n"
    # 创建年份对应的index
    index_md_content = render_events_index_md(list(event_groups.keys()))
    (target_events_dir / "index.md").write_text(index_md_content, encoding="utf8")
    written += "    - index: events/index.md\n"
    # 创建每个赛事具体的page
    for year, event_items in event_groups.items():
        cate_dir = target_events_dir / str(year)
        cate_dir.mkdir(parents=True, exist_ok=True)
        markdown = render_event_for_one_year_md(year, event_items)
        (cate_dir / "index.md").write_text(markdown, encoding="utf8")
        written += f"    - {year}:\n"
        written += f"      - index: events/{year}/index.md\n"
        for e in event_items:
            # slug = slugify_event_name(e.name)
            slug = e.id
            written += f"      - \"{e.name}\": events/{year}/{slug}.md\n"
            (cate_dir / f"{slug}.md").write_text(render_single_event_md(year, e), encoding="utf8")
    return written

logger = get_logger(__name__)
ROOT = find_project_root()

def main():
    logger.info("Generating events...")
    logger.info("Generating event IDs...")
    subprocess.run(
        ['uv', 'run', f'{ROOT}/src/scripts/setup_id.py', f'{ROOT}/src/resource/events.yml'],
        check=True  
    )
    logger.info("Generating event docs...")
    with open(ROOT / "src" / "resource" / "events.yml", "r", encoding="utf8") as file:
        events = yaml.safe_load(file)
    nav_yml_events = generate_events(
        events, 
        Path(ROOT / "docs" / "events")
    )
    
    logger.info("Events generated.")
    return nav_yml_events