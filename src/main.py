from scripts import *

if __name__ == "__main__":
    logger = get_logger(__name__)
    ROOT = find_project_root()

    logger.info(f"Generating website docs...")

    nav_yml_events = get_event_docs()
    nav_yml_tools = get_tool_docs()

    get_mkdocs_yml(nav_yml_events, nav_yml_tools)

    get_puzzle_docs()
    
    logger.info(f"All work done!")