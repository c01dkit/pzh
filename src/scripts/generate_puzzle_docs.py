import yaml
import shutil
import datetime
import re 
import os
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



def copy_template(template: Path, dest: Path):
    if dest.exists() and template.stat().st_mtime <= dest.stat().st_mtime:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, dest)

cache_event_dict = None
def get_event_index_dict():
    global cache_event_dict
    if cache_event_dict is None:
        with open(ROOT / "src" / "resources" / "events.yml", "r", encoding="utf8") as file:
            events = yaml.safe_load(file)
        events_items = create_event_items(events)
        cache_event_dict = {e.id: e for e in events_items}
    return cache_event_dict

cache_tool_dict = None
def get_tool_index_dict():
    global cache_tool_dict
    if cache_tool_dict is None:
        with open(ROOT / "src" / "resources" / "tools.yml", "r", encoding="utf8") as file:
            tools = yaml.safe_load(file)
        tools_items = create_tool_items(tools)
        cache_tool_dict = {e.id: e for e in tools_items}
    return cache_tool_dict

def render_single_puzzle_md(puzzle_item: PuzzleTemplate, appendix: str) -> str:
    """生成某个具体puzzle的界面"""
    lines: list[str] = []
    if puzzle_item.event_id:
        event_dict = get_event_index_dict()
        event_item = event_dict[puzzle_item.event_id]
    else:
        event_item = None
    lines.append(f"# {puzzle_item.title}\n")
    lines.append("=== \"简介\"")
    if puzzle_item.author:
        lines.append(f'    出题人：{puzzle_item.author}\n')
    if event_item:
        lines.append(f'    赛事来源：{event_item.name} - {event_item.subtitle} ({event_item.year})\n')
        lines.append(f"    赛事链接： [本站](/events/{event_item.year}/{event_item.id}/#{puzzle_item.title}) · [官网]({event_item.url})\n")
    if puzzle_item.round:
        lines.append(f"    题目分区：{puzzle_item.round}\n")
    if puzzle_item.note:
        lines.append(f"    备注：{puzzle_item.note}\n")
    lines.append("=== \"元提示\"")
    if puzzle_item.topics:
        lines.append(f"    题目主题：{'；'.join(puzzle_item.topics)}\n")
    if puzzle_item.tool_ids:
        tool_dict = get_tool_index_dict()
        tmp = f"    相关工具："
        for tool_id in puzzle_item.tool_ids:
            tmp += f"[{tool_dict[tool_id].name}]({tool_dict[tool_id].url}) "
        lines.append(tmp+'\n')
    if puzzle_item.extractions:
        lines.append(f"    提取方式：{'；'.join(puzzle_item.extractions)}\n")
    if lines[-1] == '=== "元提示"':
        lines.append('    该题目未见元提示。')
    lines.append("=== \"提示\"")
    for ind, hint in enumerate(puzzle_item.hints):
        lines.append(f'    ??? tip "{ind+1}. {hint.question}"')
        lines.append(f'        {hint.answer}')
    lines.append("=== \"答案\"")
    if puzzle_item.milestones:
        for ind, milestone in enumerate(puzzle_item.milestones):
            if len(milestone.phrase) > 2:
                no_blank_phrase = milestone.phrase.replace(' ', '')
                lines.append(f'    ??? info "里程碑 {ind+1}: {no_blank_phrase[0]}{"*"*(len(no_blank_phrase)-2)}{no_blank_phrase[-1]}"')
            else:
                lines.append(f'    ??? info "里程碑 {ind+1}"')
            lines.append(f'        **{milestone.phrase}** : {milestone.text}')
    else:
        lines.append('    该题目未见有里程碑。')
    lines.append(f'    ??? success "最终答案"')
    lines.append(f'        **{puzzle_item.answer}**')
    lines.append("")

    lines.append(appendix)

    return "\n".join(lines).rstrip() + "\n"

def generate_puzzles(puzzle_data:list, target_puzzles_dir:Path):
    """为docs生成单独的puzzle页面"""
    event_dict = get_event_index_dict()
    puzzle_items = create_puzzle_items(puzzle_data)
    for puzzle_item in puzzle_items:
        dest = ROOT / "src" / "resources" / "puzzles" / puzzle_item.id[:2] / puzzle_item.id / "main.md"
        if not puzzle_item.ready or not dest.exists():
            copy_template( ROOT / "src" / "resources" / "puzzles" / "template.md", dest)
        # 如果该puzzle的题解已完成，则创建对应的docs文件
        if puzzle_item.ready:
            appendix = dest.read_text(encoding="utf8")
            (target_puzzles_dir / f"{puzzle_item.id}.md").write_text(render_single_puzzle_md(puzzle_item, appendix), encoding="utf8")
        # 如果该puzzle能够对应到某赛事，则在赛事对应的markdown文件后面追加相关信息
        if puzzle_item.event_id:
            event_item = event_dict[puzzle_item.event_id]
            event_file = ROOT / "docs" / "events" / f"{event_item.year}" / f"{event_item.id}.md"
            if not event_file.exists():
                logger.warning(f"{event_file.as_posix()} should exist.")
                continue
            with event_file.open('a', encoding='utf8') as f:
                # TODO 这里要优化一下，这种写法会导致每处理一道题目，文件就要被读取写入一次
                if puzzle_item.ready:
                    f.write(f"## {puzzle_item.title}\n")
                    if puzzle_item.ft:
                        f.write(f"[{puzzle_item.ft}](/puzzles/{puzzle_item.id}/)\n")
                    else:
                        f.write(f"[本题无FT，点击此处查看题目详情。](/puzzles/{puzzle_item.id}/)\n")
                else:
                    f.write(f"## 🚧{puzzle_item.title}\n")
                    f.write(f"*题目施工中……*\n")
                f.write('\n')


logger = get_logger(__name__)
ROOT = find_project_root()

def main():
    logger.info("正在生成谜题……")
    logger.info("正在生成谜题ID……")
    config_files = next(os.walk(f'{ROOT}/src/resources/puzzle-configs'))[2]
    for config_file in config_files:
        setup_ids(f'{ROOT}/src/resources/puzzle-configs/{config_file}')
       
    logger.info("正在创建谜题模板……")
    target_puzzles_dir = ROOT / "docs" / "puzzles"
    shutil.rmtree(target_puzzles_dir, ignore_errors=True)
    target_puzzles_dir.mkdir(parents=True, exist_ok=True)
    for config_file in config_files:
        with open(ROOT / "src" / "resources" / "puzzle-configs" / config_file, "r", encoding="utf8") as file:
            puzzles = yaml.safe_load(file)
        generate_puzzles(puzzles, target_puzzles_dir)

    logger.info("谜题已完成生成。")