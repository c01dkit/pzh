import yaml
import shutil
import re 
import copy
import subprocess

from pathlib import Path
from .log import get_logger
from .utils import find_project_root

logger = get_logger(__name__)
ROOT = find_project_root()

def main(nav_yml_events, nav_yml_tools):
    logger.info("Generating mkdocs.yml...")
    web_settings = ""
    with open(ROOT / "mkdocs.yml", "r", encoding="utf8") as file:
        reach_mark = False
        for line in file:
            if not reach_mark and "# END NAV" in line:
                reach_mark = True
            if reach_mark:
                web_settings += line

    with open(ROOT / "mkdocs.yml", "w", encoding="utf8") as file:
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
        
    logger.info("mkdocs.yml generated.")
    