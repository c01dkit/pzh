from dataclasses import dataclass
import datetime


@dataclass(frozen=True)
class EventItem:
    id: str
    name: str
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
    cost: int
    question: str
    answer: str

@dataclass(frozen=True)
class MileStone:
    phrase: str
    text: str

@dataclass(frozen=True)
class PuzzleItem:
    id: str
    event_id: str
    tool_ids: list[str]
    topics: list[str] # 题目内容涉及的主题
    extractions: list[str] # 题目提取涉及的基本方式
    flavor_text: str
    question: str # 题干
    extra_urls: list[str] # 附加的链接
    image_urls: list[str]
    hints: list[HintItem]
    milestones: list[MileStone] # 里程碑
    answer: str # 答案
    solution: str # 解题思路