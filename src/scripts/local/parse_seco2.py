import requests
import pickle
import yaml
from dataclasses import dataclass


from pathlib import Path

@dataclass(frozen=True)
class HintItem:
    title: str
    content: str

@dataclass(frozen=True)
class MileStone:
    title: str
    content: str

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

def create_puzzle_items(data: list) -> list[PuzzleTemplate]:
    result = []
    for item in data:
        if item.get('title', '') == '':
            continue
        
        if item.get('hints', []):
            hints = [
                HintItem(
                    title=hint.get('title', ''),
                    content=hint.get('content', '')
                )
                for hint in item.get('hints', [])
            ]
        else:
            hints = []

        if item.get('milestones', []):
            milestones = [
                MileStone(
                    title=ms.get('title', ''),
                    content=ms.get('content', '这是本题目的一个里程碑！')
                )
                for ms in item.get('milestones', [])
            ]
        else:
            milestones = []

        result.append(
            PuzzleTemplate(
                id=item.get('id',''),
                event_id=item.get('event_id', ''),
                tool_ids=item.get('tool_ids', []),
                title=item.get('title',''),
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

cookies = {
    'cf_clearance': 'UjozHz9HRq0ylAc26z2YR8vFZn5wWL4CwlkDjjEXG0Q-1773230489-1.2.1.1-4gN9VNY4D7LTwa2CFL1P0AI6jkFPlgWSgyYccSwQWBHSe6WooTK.nP6Sf7FBBc7ppZ5jtTKEVecAq9zSJnxcm8qjBwkRsUHbhF2i8K4AkaBQDZu5LM1wBbeYv4fKDILgjWrZDmmrhI8NEqpn29Lz_4UM3rQ8WpvnM18ZPh4DFMzU7zMnH8CzejwDdP9S8sO7oFLanOX.MEFNOK_r6Ec9u9aAe3erEvi4JK9do9yPvU4',
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'priority': 'u=1, i',
    'referer': 'https://seco-archive.eterill.xyz/',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    # 'cookie': 'cf_clearance=UjozHz9HRq0ylAc26z2YR8vFZn5wWL4CwlkDjjEXG0Q-1773230489-1.2.1.1-4gN9VNY4D7LTwa2CFL1P0AI6jkFPlgWSgyYccSwQWBHSe6WooTK.nP6Sf7FBBc7ppZ5jtTKEVecAq9zSJnxcm8qjBwkRsUHbhF2i8K4AkaBQDZu5LM1wBbeYv4fKDILgjWrZDmmrhI8NEqpn29Lz_4UM3rQ8WpvnM18ZPh4DFMzU7zMnH8CzejwDdP9S8sO7oFLanOX.MEFNOK_r6Ec9u9aAe3erEvi4JK9do9yPvU4',
}

base_url = 'https://seco-archive.eterill.xyz'

with open('/home/c01dkit/github-websites/puzzlehunt/src/resources/puzzle-configs/puzzles-7d7c349ada446bf4.yml', "r", encoding="utf8") as file:
    puzzles = yaml.safe_load(file)
origin = create_puzzle_items(puzzles)
puzzle_dict = {item.title:item for item in origin}

final_embedded_list = []
for area in range(1, 8):
    acache = Path(__file__).parent / f'cache/a-{area}.pkl'
    if acache.is_file():
        response = pickle.load(acache.open('rb'))
    else:
        response = requests.get(f'{base_url}/config/seco2/area/{area}.json', cookies=cookies, headers=headers)
        pickle.dump(response, acache.open('wb'))

    data = response.json()
    temp = []
    for problem in data['problems']:
        path = problem['path']
        pindex = path.split('/')[-1]
        pcache = Path(__file__).parent / f'cache/a-{area}-p-{pindex}.pkl'
        if pcache.is_file():
            response = pickle.load(pcache.open('rb'))
        else:
            response = requests.get(f'{base_url}/config/seco2/problems/{area}/{pindex}.json', cookies=cookies, headers=headers)
            pickle.dump(response, pcache.open('wb'))
            print(f'download: area {area} problem {pindex} ({problem["title"]}) ok')

        temp.append(response.json())
    final_embedded_list.append(temp)

TEMPLATE = """- id: {id}
  event_id: {event_id}
  tool_ids: null
  title: 8番SECO
  round: 四区 - 花原
  topics: null
  author: Riser
  extractions: null
  ft: null
  note: null
  hints:
  - question: 我毫无头绪！
    answer: null
  - question: 该如何提取？
    answer: null
  milestones: null
  answer: PERFUMED
  ready: false"""

def _needs_quoting(s: str) -> bool:
    """判断一个 YAML 纯量字符串是否需要用单引号包裹。"""
    if not s:
        return False
    # 行首出现这些 ASCII 字符时 YAML 会产生歧义
    if s[0] in '*&!{[|>\'":%,#@`?-':
        return True
    # '&' 在任意位置均表示锚点
    if '&' in s:
        return True
    # ': ' 会被误读为映射分隔符
    if ': ' in s:
        return True
    # ' #' 起内联注释
    if ' #' in s:
        return True
    # YAML 保留字
    if s.lower() in ('true', 'false', 'null', 'yes', 'no', 'on', 'off'):
        return True
    return False


def _scalar(v) -> str:
    """将 Python 值序列化为 YAML 纯量 token。"""
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    s = v if isinstance(v, str) else str(v)
    if _needs_quoting(s):
        return "'" + s.replace("'", "''") + "'"   # 单引号内部转义
    return s

# 输出字段顺序（与数据类定义顺序不同）
_FIELD_ORDER = [
    'id', 'event_id', 'tool_ids', 'title', 'round', 'topics',
    'author', 'extractions', 'ft', 'note', 'hints', 'milestones',
    'answer', 'ready',
]

# 值为 list[str] | None 的普通列表字段
_LIST_SCALAR_FIELDS = {'tool_ids', 'topics', 'extractions'}

def _puzzle_to_lines(puzzle: PuzzleTemplate) -> list[str]:
    """将单个 PuzzleTemplate 序列化为 YAML 行列表（作为顶层列表的一项）。"""
    lines: list[str] = []

    for idx, field in enumerate(_FIELD_ORDER):
        v = getattr(puzzle, field)
        lead = '- ' if idx == 0 else '  '   # 第一个字段用 '- '，其余缩进 2 格

        # ── list[str] 类字段 ──────────────────────────────────────────────────
        if field in _LIST_SCALAR_FIELDS:
            if not v:                              # None 或空列表 → null
                lines.append(f'{lead}{field}: null')
            else:
                lines.append(f'{lead}{field}:')
                for item in v:
                    lines.append(f'  - {_scalar(item)}')

        # ── hints ─────────────────────────────────────────────────────────────
        elif field == 'hints':
            if not v:
                lines.append(f'{lead}{field}: null')
            else:
                lines.append(f'{lead}{field}:')
                for hint in v:
                    lines.append(f'  - title: {_scalar(hint.title)}')
                    lines.append(f'    content: {_scalar(hint.content)}')

        # ── milestones ────────────────────────────────────────────────────────
        elif field == 'milestones':
            if v is None:
                lines.append(f'{lead}{field}: null')
            else:
                lines.append(f'{lead}{field}:')
                for ms in v:
                    lines.append(f'  - title: {_scalar(ms.title)}')
                    if ms.content:                    # content 为空时省略
                        lines.append(f'    content: {_scalar(ms.content)}')

        # ── 普通标量字段（str / bool / None）────────────────────────────────
        else:
            if v is None:
                lines.append(f'{lead}{field}: null')
            else:
                lines.append(f'{lead}{field}: {_scalar(v)}')

    return lines

def puzzle_templates_to_yaml(puzzles: list[PuzzleTemplate]) -> str:
    """将 PuzzleTemplate 列表序列化为 YAML 字符串。"""
    lines: list[str] = []
    for puzzle in puzzles:
        lines.extend(_puzzle_to_lines(puzzle))
    return '\n'.join(lines)


def print_puzzle_templates(puzzles: list[PuzzleTemplate]) -> None:
    """将 PuzzleTemplate 列表以 YAML 形式打印到标准输出。"""
    print(puzzle_templates_to_yaml(puzzles))

def parse(item: PuzzleTemplate, puzzle: dict):
    def newft(s:str):
        s = s.replace('<font color=\"#808080\">','').replace('</font>','')
        s = s.replace('<p>', '').replace('</p>','').replace('\\n',' ').replace('\n',' ')
        s = s.replace('</strong>','').replace('<strong>','')
        s = s.replace('<i>','*').replace('</i>','*')
        s = s.replace('&emsp;','&emsp;&emsp;')
        return s
    # if item.id == '2446459fc577d4d5':
    #     print(puzzle)
    return PuzzleTemplate(
        id=item.id,
        event_id=item.event_id,
        tool_ids=item.tool_ids,
        title=item.title,
        note='',
        round=item.round,
        author=item.author,
        ft=newft(puzzle['desc']) if not item.ready else item.ft,
        topics=item.topics,
        extractions=item.extractions,
        hints=[HintItem(title=i['title'].replace('\\n',' ').replace('\n',' '), content=i['content'].replace('\\n',' ').replace('\n',' ')) for i in puzzle['tips']],
        milestones=[MileStone(title=i['answer'].replace('\\n',' ').replace('\n',' '), content=i['message'].replace('\\n',' ').replace('\n',' ')) for i in puzzle['additionalAnswers']],
        answer=item.answer,
        ready=item.ready,
    )

ddd = []
for area_puzzles in final_embedded_list:
    for puzzle in area_puzzles:
        if puzzle['title'] not in puzzle_dict:
            print(puzzle['title'])
        else:
            puzzle_item = puzzle_dict[puzzle['title']]
            new_item = parse(puzzle_item, puzzle)
            ddd.append(new_item)

# final meta不在的。需要自己补充一下
print_puzzle_templates(ddd)
                
