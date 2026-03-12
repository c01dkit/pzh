import yaml
import shutil
import datetime
import re 
import os
import copy
import subprocess

from pathlib import Path
from .log import get_logger
from .utils import find_project_root, slugify_dirname
from .models import *
from . import setup_ids

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





def create_event_groups(event_items:list[EventItem]) -> dict[str, list[EventItem]]:
    result = {}
    for event in event_items:
        result.setdefault(event.year, []).append(event)
        # logger.debug(f"{event.start_time} is {type(event.start_time)}, {event.end_time} is {type(event.end_time)}")
    for k in result:
        result[k].sort(key=lambda x: (datetime.datetime.max if x.start_time is None else x.start_time, x.name.lower()), reverse=True)
    return dict(sorted(result.items(), key=lambda x: x[0], reverse=True))

def render_events_index_md(categories: list[str]) -> str:
    """生成赛事总览中包含各个年份链接的总index"""
    lines: list[str] = []
    lines.append("# 赛事总览\n")
    lines.append("按年份整理的赛事链接。赛事名称前使用以下标记表示该赛事谜题收录情况：\n")
    lines.append("* 🟢 该赛事谜题及题解已收录\n")
    lines.append("* 🟠 该赛事谜题及题解正在收录中\n")
    lines.append("* 🔴 该赛事谜题及题解尚未收录\n")
    lines.append("## 年份\n")
    for cat in categories:
        slug = slugify_dirname(str(cat))
        lines.append(f"- [{cat}](./{slug}/index.md)")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def render_event_for_one_year_md(year: str, items: list[EventItem]) -> str:
    """生成某年所有赛事的index界面"""
    lines: list[str] = []
    months = set()
    lines.append(f"# {year}年赛事")
    lines.append("")
    for event_item in items:
        name = event_item.name
        start_time = event_item.start_time.strftime("%Y-%m-%d %H:%M") if event_item.start_time else None
        end_time = event_item.end_time.strftime("%Y-%m-%d %H:%M") if event_item.end_time else None
        host = event_item.host or ""
        if event_item.start_time:
            if event_item.start_time.month not in months:
                lines.append(f'## {event_item.start_time.month}月赛事\n')
                lines.append('---\n')
                months.add(event_item.start_time.month)
        elif '其他' not in months:
            lines.append(f'## 其他赛事\n')
            lines.append('---\n')
            months.add('其他')
        lines.append(f"### {name}")
        
        # 比赛时间、主办方、网址
        if event_item.subtitle:
            lines.append(f"- 主题：{event_item.subtitle}")
        if start_time and end_time:
            lines.append(f"- 时间：{start_time} ～ {end_time}")
        elif start_time:
            lines.append(f"- 时间：{start_time}")
        if host:
            lines.append(f"- 主办方：{host}")
        if event_item.url:
            lines.append(f"- 网站链接：[本站](/events/{event_item.year}/{event_item.id}/) · [官网]({event_item.url})")
        else:
            lines.append(f"- 网站链接：[本站](/events/{event_item.year}/{event_item.id}/) · 官网链接已失效")

        if event_item.description:
            lines.append("")
            lines.append(md_escape(event_item.description))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def render_single_event_md(year: str, event_item: EventItem) -> str:
    """生成某个具体赛事的界面"""
    lines: list[str] = []
    name = event_item.name
    start_time = event_item.start_time.strftime("%Y-%m-%d %H:%M") if isinstance(event_item.start_time, datetime.datetime) else None
    end_time = event_item.end_time.strftime("%Y-%m-%d %H:%M") if isinstance(event_item.end_time, datetime.datetime) else None
    host = event_item.host or ""

    lines.append(f"# {name}")
    

    # 比赛主题、时间、主办方、网址
    if event_item.subtitle:
        lines.append(f"- 主题：{event_item.subtitle}")
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

    return "\n".join(lines).rstrip() + "\n\n"

def get_event_status_dict():
    event_status_dict: dict[str, list[int, int]] = {} # event_id -> [finished puzzle cnt, all puzzle cnt]
    config_files = next(os.walk(f'{ROOT}/src/resources/puzzle-configs'))[2]
    for config_file in config_files:
        with open(f'{ROOT}/src/resources/puzzle-configs/{config_file}', "r", encoding="utf8") as file:
            puzzles = yaml.safe_load(file)
        puzzle_items = create_puzzle_items(puzzles)
        for puzzle_item in puzzle_items:
            if puzzle_item.event_id:
                event_status_dict.setdefault(puzzle_item.event_id, [0, 0])
                event_status_dict[puzzle_item.event_id][1] += 1
                if puzzle_item.ready:
                    event_status_dict[puzzle_item.event_id][0] += 1
    return event_status_dict

def generate_events(events_data:list, target_events_dir:Path) -> str:
    """在指定目录中生成以年份进行分组的赛事子文件夹，返回对应需要填写在nav里的str
    """
    shutil.rmtree(target_events_dir, ignore_errors=True)
    target_events_dir.mkdir(parents=True, exist_ok=True)
    event_items = create_event_items(events_data)
    event_groups = create_event_groups(event_items)
    event_status_dict = get_event_status_dict()

    written = "  - 赛事总览:\n"
    # 创建年份对应的index
    index_md_content = render_events_index_md(list(event_groups.keys()))
    (target_events_dir / "index.md").write_text(index_md_content, encoding="utf8")
    written += "    - events/index.md\n"
    # 创建每个赛事具体的page
    for year, event_items in event_groups.items():
        cate_dir = target_events_dir / str(year)
        cate_dir.mkdir(parents=True, exist_ok=True)
        markdown = render_event_for_one_year_md(year, event_items)
        (cate_dir / "index.md").write_text(markdown, encoding="utf8")
        written += f"    - {year}:\n"
        written += f"      - events/{year}/index.md\n"
        for e in event_items:
            # slug = slugify_event_name(e.name)
            slug = e.id
            es = event_status_dict.get(e.id, None)
            if es:
                if es[0] == es[1]:
                    written += f"      - \"🟢 {e.name}\": events/{year}/{slug}.md\n"
                else:
                    written += f"      - \"🟠 {e.name}\": events/{year}/{slug}.md\n"
            else:
                written += f"      - \"🔴 {e.name}\": events/{year}/{slug}.md\n"
            (cate_dir / f"{slug}.md").write_text(render_single_event_md(year, e), encoding="utf8")
    return written

logger = get_logger(__name__)
ROOT = find_project_root()

def main():
    logger.info("正在生成赛事……")
    logger.info("正在生成赛事ID……")
    setup_ids(f'{ROOT}/src/resources/events.yml')
    logger.info("正在生成赛事文档……")
    with open(ROOT / "src" / "resources" / "events.yml", "r", encoding="utf8") as file:
        events = yaml.safe_load(file)
    nav_yml_events = generate_events(
        events, 
        Path(ROOT / "docs" / "events")
    )
    
    logger.info("赛事已完成生成。")
    return nav_yml_events