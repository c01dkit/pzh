import re
from pathlib import Path

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