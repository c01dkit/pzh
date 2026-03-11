import re
import os
import yaml
import shutil
from pathlib import Path
from .models import *

def find_project_root(marker: str = "mkdocs.yml") -> Path:
    current = Path(__file__).resolve().parent
    while True:
        if (current / marker).exists():
            return current
        parent = current.parent
        if parent == current:
            # 已到达文件系统根目录，仍未找到
            raise FileNotFoundError(f"找不到包含 {marker} 的项目根目录")
        current = parent

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


def replace_img_lines(
    text: str,
    img_pattern: str = '![alt text](Snipaste',
    repo_base: str = "https://github.com/c01dkit/pzh/blob/main/docs/assets/images/"
) -> str:
    """
    扫描文本的每一行：
      - 若某一行包含img_pattern
        则其替换为: ![img]({repo_base}{old_prefix}
    """
    out_lines = []
    for line in text.splitlines(keepends=True):
        if img_pattern in line:
            old_prefix = img_pattern.split('(')[-1]
            line = line.replace(img_pattern, f'![img]({repo_base}{old_prefix}')
            line = re.sub(rf'{old_prefix}(.*?)\)',rf'{old_prefix}\1?raw=true)',line)
        out_lines.append(line)
    return "".join(out_lines)


def copy_template(template: Path, dest: Path):
    if dest.exists() and template.stat().st_mtime <= dest.stat().st_mtime:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, dest)

ROOT = find_project_root()

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

