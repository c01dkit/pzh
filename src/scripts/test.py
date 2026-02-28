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

qu = ""
quname = ""
state = 0

template = """- id: 
  event_id: 7d7c349ada446bf4
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
        print(template.format(author=author,title=title,round=round,answer=answer))