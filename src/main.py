from scripts import *

if __name__ == "__main__":
    logger = get_logger(__name__)
    ROOT = find_project_root()

    logger.info(f"正在生成docs文档...")

    nav_yml_events = get_event_docs()
    nav_yml_tools = get_tool_docs()
    nav_yml_puzzles = get_puzzle_docs()

    get_mkdocs_yml(nav_yml_events, nav_yml_puzzles, nav_yml_tools)

    
    logger.info(f"所有工作顺利完成！")