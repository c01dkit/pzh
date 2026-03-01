from pathlib import Path
from .log import get_logger

qu = ""
quname = ""
state = 0

template = """- id: 
  event_id: {event_id}
  tool_ids: null
  title: {title}
  round: {round}
  topics: null
  author: {author}
  extractions: null
  ft: null
  note: null
  hints:
  - question: 我毫无头绪！
    answer: 
  - question: 该如何提取？
    answer: 
  milestones: null
  answer: {answer}
  ready: false"""
author = title = round = answer = ""

def get_7d7c349ada446bf4(event_id):
    s = """一区
庄园
新手教程
CEMETERY
出题人：Riser
数码方阵
CHIPS
出题人：纪录片
坏苹果！！
SUIKA
出题人：Light
中英互译Plus
TORCH
出题人：Riser
童话故事
FOG
出题人：Riser
？？？？Plus
CANNON
出题人：Riser
认字是门化简为繁的技术
CHRYSANTHEMUM
出题人：WAHX
拼图
SECTION
出题人：Riser
二区
沙海
3 small mazes
WINTER
出题人：Lana
解绳子
POPCORN
出题人：Riser
调色盘
VANGOGH
出题人：Light
差序格局Plus
TANGELA
出题人：WAHX
长河漫漫，当文物醒来…
CONJOINT
出题人：King
对对碰
DOUBLE
出题人：Light
程式之衡鉴
CAT
出题人：Riser
疯狂星期四
GOBBLE
出题人：WAHX
见微知微
DESERT
出题人：Lana
中国话
CAFES
出题人：WAHX/Light
数字狂想曲
VEGETABLE
出题人：半次获释者
六八一十二
MINIGUN
出题人：磬绿薄绒荷
道是无情却有晴
PENTAGRAM
出题人：Light
四线格
HALLOWEEN
出题人：Light
移言为定
MARINE
出题人：Lana
先天与后天
MENDEL
出题人：Light
Wordles
BECOMING
出题人：Riser
三区
高塔
未知图腾？
STEEL
出题人：嘉和逆天
知识速记
GREAT WALL
出题人：Riser
本题使用人工智能...
SCARE
出题人：Light
多重数独
TEARS
出题人：Riser
到底是谁炸的群！
FLATTEN
出题人：Light
还在go
TOMORIN
出题人：Light
游戏误学习
MYCENA
出题人：Riser
十诀
BOWLING
出题人：Light
看！听！提！
APOCALYPSE
出题人：Riser
宝可梦家族
BROTHERS
出题人：嘉和逆天
烂柯人观棋记
NELUMBO
出题人：WAHX
一一对应
FRIENDSHIP
出题人：纪录片/Riser
四区
花原
联络处
ATTRACTION
出题人：Lana
声・韵・调
SNOW
出题人：Lana
8番SECO
PERFUMED
出题人：Riser
像素小游戏
PUFF
出题人：Light
盲人摸字
CROSSFIRE
出题人：WAHX
f(字)
COPSY
出题人：Lana
随蓝百练
ICE BOMB
出题人：WAHX
Mini Linker
DUKE CHERRY
出题人：半次获释者/King
朝复夕
TRIPLETS
出题人：Lana
八方来词
PSYCHOL
出题人：WAHX/花落星飞/小汤圆
雪崩
BLUE
出题人：Lana
定量分析
AFFLUENT
出题人：Lana
谷歌翻译
UMBRELLA
出题人：花落星飞
画布之间
MONOCHROME
出题人：半次获释者/Riser
五区 & 过渡
暗格 / 过渡
我的世界
PLANTING
出题人：Riser
规则怪谈
PVZPENNY
出题人：Riser
我来秋浦正逢秋
ALIEN
出题人：WAHX
六区
中心
将胡解谜
COLOR MIXED
出题人：Lana
SECO2-DLC
RUINED TOWERS HISTORY
出题人：WAHX/嘉和逆天/Light/桑丘
机关塔
ISLE
出题人：嘉和逆天
Bingo!
SPLIT PERSONALITY
出题人：Riser
暗格
WATER CYCLE
出题人：WAHX/盐铁桶子/琳儿
循环
CENTER PIECE
出题人：Riser
Final
终局
FM
SECOND CHANCE
出题人：Riser"""
    target_file = ROOT/"src"/"resources"/"puzzle-configs"/f"puzzles-{event_id}.yml"
    if target_file.exists():
        logger.critical(f"目标文件{target_file.name}已存在！")
        return
    output_file = open(target_file, 'w', encoding='utf8')    
    for line in s.splitlines():
        if '区' in line or 'Final' in line:
            qu = line
            state = 1
            continue
        if state == 1:
            round = f'{qu} - {line}'
            state = 2
        elif state == 2:
            title = line
            state = 3
        elif state == 3:
            answer = line
            state = 4
        elif state == 4:
            author = line.split('：')[-1]
            state = 2
            print(template.format(author=author,title=title,round=round,answer=answer,event_id=event_id),file=output_file)
    output_file.close()
    
def get_4948bf9479046558(event_id):
    s = """1	无孔不入的填字游戏
113次解决 | 356次猜测 | 149支队伍
解析	
DOORINTERLOCK
2	年夜饭
234次解决 | 372次猜测 | 236支队伍
解析	
SKYRAIN
3	抢红包
196次解决 | 814次猜测 | 203支队伍
解析	
WECHATREDPACKETS
4	画马
124次解决 | 712次猜测 | 152支队伍
解析	
BEIJINGOLYMPIC
5	推箱字
211次解决 | 249次猜测 | 212支队伍
解析	
CHINACOLOUR
6	对酒当歌
156次解决 | 304次猜测 | 169支队伍
解析	
ALLBEERHERE
7	两灯一谜对连
181次解决 | 477次猜测 | 187支队伍
解析	
DIALECTS
8	物薄情厚
115次解决 | 508次猜测 | 144支队伍
解析	
EXPRESSDELIVERY
9	田忌赛马
186次解决 | 345次猜测 | 186支队伍
解析	
YOUNGTOOLD
10	地下旅行
157次解决 | 481次猜测 | 166支队伍
解析	
ELLIPSE
11	方形田字
141次解决 | 783次猜测 | 158支队伍
解析	
HOURLYCHARGE
12	所罗门王的钥匙
56次解决 | 405次猜测 | 117支队伍
解析	
LOGINCREDENTIAL
meta 一年又一年
167次解决 | 1571次猜测 | 168支队伍
解析	
INLUCKYSPELL
彩蛋-A puzzle only with meta
123次解决 | 508次猜测 | 128支队伍
解析	
becomericher"""
    state = 1
    target_file = ROOT/"src"/"resources"/"puzzle-configs"/f"puzzles-{event_id}.yml"
    if target_file.exists():
        logger.critical(f"目标文件{target_file.name}已存在！")
        return
    output_file = open(target_file, 'w', encoding='utf8')
    for line in s.splitlines():
        if state == 1:
            title = line.split('\t')[-1]
            state = 2
        elif state == 2:
            # title = line
            state = 3
        elif state == 3:
            # answer = line
            state = 4
        elif state == 4:
            answer = line
            state = 1
            print(template.format(author=author,title=title,round=round,answer=answer,event_id=event_id),file=output_file)
    output_file.close()


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

if __name__ == '__main__':
    ROOT = find_project_root()
    logger = get_logger(__name__)
    # get_7d7c349ada446bf4('7d7c349ada446bf4') # [2026] seco2 
    get_4948bf9479046558('4948bf9479046558') # [2026] 欣年3