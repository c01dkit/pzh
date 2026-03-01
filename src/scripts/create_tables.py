s = """1	北京	费马大定理	FERMAT'S LAST THEOREM	(10/6'1 4 7)	S
2	石家庄	海马	SEAHORSE	(2/8)	E
3	西安	马化腾	PONY MA	(3/4 2)	N
4	郑州	马德堡半球	MAGDEBURG HEMISPHERES	(4/9 11)	D
5	武汉	马池	MACHI	(2/5)	A
6	重庆	马拉松	MARATHON	(6/8)	H
7	南昌	罗马数字	ROMAN NUMERAL	(2/5 7)	O
8	杭州	马达加斯加	MADAGASCAR	(10/10)	R
9	上海	马蹄铁	HORSESHOE	(6/9)	S
10	青岛	马口铁	TIN PLATE	(8/3 5)	E"""


print('| 线索 | 解答 | 备注 |')
print('| --- | --- | --- |')

for line in s.splitlines():
    if len(line) < 1:
        continue
    li = line.split('\t')
    print('|',end="")
    for i in li:
        if len(i) == 0:
            continue
        print(f" {i} |",end='')
    print('  |')
    # print('')
