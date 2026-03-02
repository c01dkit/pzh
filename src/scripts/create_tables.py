s = """DOOR INTERLOCK	开锁	2008	戊子	5	1	I
BEIJING OLYMPIC	北京欢迎你	2009	己丑	6	2	N
ALL BEER HERE	羊肉串	1986	丙寅	3	3	L
CHINA COLOUR	满庭芳·国色	2023	癸卯	10	4	U
HOURLY CHARGE	钟点工	2000	庚辰	7	5	C
SKYRAIN	借伞	2025	乙巳	2	6	K
YOUNG TO OLD	时间都去哪儿了	2014	甲午	1	7	Y
DIALECTS	乡音	1991	辛未	8	8	S
EXPRESS DELIVERY	快递小乔	2016	丙申	3	9	P
WECHAT RED PACKETS	恭喜发财	2005	乙酉	2	10	E
LOGIN CREDENTIAL	密码	1994	甲戌	1	11	L
ELLIPSE	找焦点	1995	乙亥	2	12	L"""


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
