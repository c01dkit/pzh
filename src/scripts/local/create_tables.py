s = """费XX	马寅初	13
冯XX	吴震春	3
何XX	蒋梦麟	8
梅XX	郭任远	1
任XX	潘云鹤	15
许XX	吴朝晖	14
张XX	韩祯祥	9
宗XX	霍士廉	16"""



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
