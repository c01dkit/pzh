import yaml
import shutil
import datetime
import re 
import os
import subprocess

from pathlib import Path
from .log import get_logger
from .utils import *
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
        if event_item.url:
            lines.append(f'    赛事来源：[{event_item.name} - {event_item.subtitle} ({event_item.year})]({event_item.url})\n')
        else:
            lines.append(f'    赛事来源：{event_item.name} - {event_item.subtitle} ({event_item.year})\n')
        lines.append(f"    本站导航： [返回到当前赛事页面](/events/{event_item.year}/{event_item.id}/#{puzzle_item.title})\n")
    if puzzle_item.round:
        lines.append(f"    题目分区：{puzzle_item.round}\n")
    if puzzle_item.note:
        lines.append(f"    备注：{puzzle_item.note}\n")
    lines.append("=== \"元提示\"")
    lines.append("    ??? danger \"剧透警告\"")
    if puzzle_item.topics:
        lines.append(f"        题目主题：{'；'.join(puzzle_item.topics)}\n")
    if puzzle_item.tool_ids:
        tool_dict = get_tool_index_dict()
        tmp = f"        相关工具："
        for tool_id in puzzle_item.tool_ids:
            tmp += f"[{tool_dict[tool_id].name}]({tool_dict[tool_id].url}) "
        lines.append(tmp+'\n')
    if puzzle_item.extractions:
        lines.append(f"        提取方式：{'；'.join(puzzle_item.extractions)}\n")
    if lines[-1] == '=== "元提示"':
        lines.append('        该题目未见元提示。\n')
    lines.append("=== \"提示\"")
    for ind, hint in enumerate(puzzle_item.hints):
        lines.append(f'    ??? tip "{ind+1}. {hint.title}"')
        lines.append(f'        {hint.content}')
    lines.append("\n=== \"答案\"")
    if puzzle_item.milestones:
        for ind, milestone in enumerate(puzzle_item.milestones):
            if len(str(milestone.title)) > 2:
                no_blank_phrase = milestone.title.replace(' ', '')
                lines.append(f'    ??? info "里程碑 {ind+1}: {no_blank_phrase[0]}{"\\*"*(len(no_blank_phrase)-2)}{no_blank_phrase[-1]}"')
            else:
                lines.append(f'    ??? info "里程碑 {ind+1}"')
            lines.append(f'        **{milestone.title}** : {milestone.content}')
    else:
        lines.append('    !!! info ""')
        lines.append('        该题目未见有里程碑')
    lines.append(f'    ??? success "最终答案"')
    lines.append(f'        **{puzzle_item.answer}**')
    lines.append("")

    lines.append(replace_img_lines(
        appendix,
        img_pattern = '![alt text](Snipaste',
        repo_base= f"https://github.com/c01dkit/pzh/blob/main/src/resources/puzzles/{puzzle_item.id[:2]}/{puzzle_item.id}/"
        )
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_puzzles_single_event(puzzle_data:list, target_puzzles_dir:Path):
    """为docs生成单独的puzzle页面"""
    event_dict = get_event_index_dict()
    puzzle_items = create_puzzle_items(puzzle_data)
    file_appends: dict[Path, list[str]] = {}  # filename -> [lines]
    event_rounds: dict[str, set] = {}
    for puzzle_item in puzzle_items:
        # 如果尚未编写题解，则创建题解模板
        dest = ROOT / "src" / "resources" / "puzzles" / puzzle_item.id[:2] / puzzle_item.id / "main.md"
        if not puzzle_item.ready or not dest.exists():
            copy_template( ROOT / "src" / "resources" / "puzzles" / "template.md", dest)
        # 如果该puzzle的题解已完成，则创建对应的docs文件，并将其添加到nav_yml里
        if puzzle_item.ready:
            appendix = dest.read_text(encoding="utf8")
            (target_puzzles_dir / f"{puzzle_item.id}.md").write_text(render_single_puzzle_md(puzzle_item, appendix), encoding="utf8")
        # 如果该puzzle能够对应到某赛事，则在赛事对应的markdown文件后面追加相关信息
        if puzzle_item.event_id:
            event_item = event_dict[puzzle_item.event_id]
            event_file = ROOT / "docs" / "events" / f"{event_item.year}" / f"{event_item.id}.md"
            if not event_file.exists():
                logger.warning(f"赛事文件{event_file.as_posix()}未找到")
                continue
            file_appends.setdefault(event_file,[])
            event_rounds.setdefault(event_item.id, set())
            if puzzle_item.round:
                if puzzle_item.round not in event_rounds[event_item.id]:
                    file_appends[event_file].append(f'## {puzzle_item.round}\n\n---\n\n')
                    event_rounds[event_item.id].add(puzzle_item.round)
                if puzzle_item.ready:
                    file_appends[event_file].append(f'### {puzzle_item.title}\n')
                    if puzzle_item.ft:
                        file_appends[event_file].append(f"[{puzzle_item.ft}](/puzzles/{puzzle_item.id}/)\n")
                    else:
                        file_appends[event_file].append(f"[本题无FT，点击此处查看题目详情。](/puzzles/{puzzle_item.id}/)\n")
                else:
                    file_appends[event_file].append(f'### 🚧{puzzle_item.title}\n')
                    file_appends[event_file].append(f'*题目施工中……*\n')
            else:
                if puzzle_item.ready:
                    file_appends[event_file].append(f'## {puzzle_item.title}\n')
                    if puzzle_item.ft:
                        file_appends[event_file].append(f"[{puzzle_item.ft}](/puzzles/{puzzle_item.id}/)\n")
                    else:
                        file_appends[event_file].append(f"[本题无FT，点击此处查看题目详情。](/puzzles/{puzzle_item.id}/)\n")
                else:
                    file_appends[event_file].append(f'## 🚧{puzzle_item.title}')
                    file_appends[event_file].append(f'*题目施工中……*\n')
            file_appends[event_file].append('\n')
            
    for file, lines in file_appends.items():
        with open(file, 'a', encoding='utf8') as f:
            f.writelines(lines)
    return puzzle_items


def render_puzzle_index_md(puzzle_items_dict: dict[str, list[PuzzleTemplate]]) -> str:
    """生成题目总览中各个赛事主题的总index"""
    lines: list[str] = []
    lines.append("# 题目总览\n")
    lines.append("按主题整理的题目链接。\n")
    lines.append("!!! danger \"剧透警告\"")
    lines.append("    根据题面推断主题也是解密过程中的一环。为保证完整的游玩体验，请谨慎浏览此页面。\n")
    for topic, puzzle_items in puzzle_items_dict.items():
        lines.append(f'## {topic}\n')
        for puzzle_item in puzzle_items:
            if puzzle_item.topics and len(puzzle_item.topics) >= 2:
                lines.append(f"- [{'/'.join(puzzle_item.topics[1:])}] [{puzzle_item.title}](/puzzles/{puzzle_item.id}/)")
            else:
                lines.append(f"- [{puzzle_item.title}](/puzzles/{puzzle_item.id}/)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

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

    written = "  - 题目总览:\n"
    written += '    - puzzles/index.md\n'
    puzzle_dict = {'其他':[]}
    for config_file in config_files:
        with open(ROOT / "src" / "resources" / "puzzle-configs" / config_file, "r", encoding="utf8") as file:
            puzzles = yaml.safe_load(file)
        puzzle_items = generate_puzzles_single_event(puzzles, target_puzzles_dir)
        for puzzle_item in puzzle_items:
            if puzzle_item.ready:
                if puzzle_item.topics:
                    topic = puzzle_item.topics[0]
                    puzzle_dict.setdefault(topic,[])
                    puzzle_dict[topic].append(puzzle_item)
                else:
                    puzzle_dict["其他"].append(puzzle_item)
    priority = {"其他": 2}
    puzzle_dict = dict(sorted(puzzle_dict.items(), key=lambda x: (priority.get(x[0], 1), x[0].lower())))
    for topic, items in puzzle_dict.items():
        written += f'    - {topic}:\n'
        for puzzle_item in items:
            written += f'      - "{puzzle_item.title}": puzzles/{puzzle_item.id}.md\n'
    index_md_content = render_puzzle_index_md(puzzle_dict)
    (target_puzzles_dir / "index.md").write_text(index_md_content, encoding="utf8")
    logger.info("谜题已完成生成。")
    return written
