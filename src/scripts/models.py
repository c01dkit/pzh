from dataclasses import dataclass
from .log import get_logger
import datetime


@dataclass(frozen=True)
class EventItem:
    id: str
    name: str
    subtitle: str
    url: str
    description: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    year: int
    host: str
    tags: list[str]

@dataclass(frozen=True)
class ToolItem:
    id: str
    name: str
    url: str
    description: str
    category: list[str]
    tags: list[str]

@dataclass(frozen=True)
class HintItem:
    question: str
    answer: str

@dataclass(frozen=True)
class MileStone:
    phrase: str
    text: str

@dataclass(frozen=True)
class PuzzleTemplate:
    id: str
    event_id: str
    tool_ids: list[str]
    title: str
    note: str # 一些备注，用于说明整合到本网站的信息扭曲
    round: str
    author: str # 出题人
    ft: str
    topics: list[str] # 题目内容涉及的主题
    extractions: list[str] # 题目提取涉及的基本方式
    hints: list[HintItem]
    milestones: list[MileStone] # 里程碑
    answer: str # 答案
    ready: bool # 是否能呈现到最后生成的网站中

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
                subtitle=item.get('subtitle',''),
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

def create_puzzle_items(data: list) -> list[PuzzleTemplate]:
    result = []
    for item in data:
        if item.get('title', '') == '':
            logger.warning("PuzzleTemplate with missing title found")
            continue
        
        if item.get('hints', []):
            hints = [
                HintItem(
                    question=hint.get('question', ''),
                    answer=hint.get('answer', '')
                )
                for hint in item.get('hints', [])
            ]
        else:
            hints = []

        if item.get('milestones', []):
            milestones = [
                MileStone(
                    phrase=ms.get('phrase', ''),
                    text=ms.get('text', '这是本题目的一个里程碑！')
                )
                for ms in item.get('milestones', [])
            ]
        else:
            milestones = []

        result.append(
            PuzzleTemplate(
                id=item.get('id'),
                event_id=item.get('event_id', ''),
                tool_ids=item.get('tool_ids', []),
                title=item.get('title'),
                note=item.get('note', ''),
                author=item.get('author', ''),
                ft = item.get('ft', ''),
                round=item.get('round', ''),
                topics=item.get('topics', []),
                extractions=item.get('extractions', []),
                hints=hints,
                milestones=milestones,
                answer=item.get('answer', ''),
                ready=item.get('ready', False),
            )
        )
    return result

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


logger = get_logger(__name__)