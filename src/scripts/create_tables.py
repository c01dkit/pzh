s = """梦之旅	dream journey	N
黄金船	gold ship	O
草上飞	grass wonder	L
美丽周日	marvelous sunday	Y
优秀素质	nice nature	O
米浴	rice shower	T
醒目飞鹰	smart falcon	O
特别周	special week	G
玉藻十字	tamamo cross	U
双涡轮	twin turbo	D"""


print('| 序号 | 线索 | 解答 | 备注 |')
print('| --- | --- | --- | --- |')

for line in s.splitlines():
    if len(line) < 1:
        continue
    li = line.split('\t')
    print('|',end="")
    for i in li:
        if len(i) == 0:
            continue
        print(f" {i} |",end='')
    # print('  |')
    print('')
