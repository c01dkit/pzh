import yaml
import shutil
import datetime
import re 
import copy
import subprocess

from pathlib import Path
from .log import get_logger
from .utils import find_project_root, slugify_dirname
from .models import ToolItem



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
                id=item.get('id'),
                name=item.get('name'),
                url = item.get('url'),
                description=item.get('description'),
                category=category,
                tags=item.get('tags', [])
            )
        )
    return result

def create_tool_groups(tool_items: list[ToolItem]) -> dict[str, list[ToolItem]]:
    result = {}
    for tool in tool_items:
        for cate in tool.category:
            result.setdefault(cate, []).append(tool)
    for cate in result:
        result[cate].sort(key=lambda x: x.name.lower())

    priority = {"必备": 0, "工具杂项类": 2, "其他杂项类": 3}
    return dict(sorted(result.items(), key=lambda x: (priority.get(x[0], 1), x[0].lower())))





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

logger = get_logger(__name__)
ROOT = find_project_root()

def main():
    logger.info("Generating tools...")
    logger.info("Generating tool IDs...")
    subprocess.run(
        ['uv', 'run', f'{ROOT}/src/scripts/setup_id.py', f'{ROOT}/src/resource/tools.yml'],
        check=True  
    )
    logger.info("Generating tool docs...")
    with open(ROOT / "src" / "resource" / "tools.yml", "r", encoding="utf8") as file:
        tools = yaml.safe_load(file)
    nav_yml_tools = generate_tools(
        tools,
        Path(ROOT / "docs" / "tools")
    )
    logger.info("Tools generated.")
    return nav_yml_tools