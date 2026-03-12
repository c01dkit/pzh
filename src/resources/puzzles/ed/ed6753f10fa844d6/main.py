from lxml import html
from pathlib import Path
from pydantic import BaseModel
from collections import defaultdict

class Metro(BaseModel):
    district: str
    lineName: str
    hexColor: str | None
    rgbColor: tuple[int, int, int] | None


def parse_rgb(text: str):
    text = ''.join(filter(lambda x: x in '0123456789,', text))
    if len(text) < 3:
        return None
    parts = [x.strip() for x in text.split(",")]
    if len(parts) != 3:
        return None
    try:
        tuple(map(int, parts))
    except:
        print(f'请检查html文件中{parts}（对应{text}）颜色是否有误。')
        return None
    return  tuple(map(int, parts))# type: ignore

def normalize_hex_color(color: str) -> str:
    color = color.strip().upper()
    if not color.startswith("#"):
        color = "#" + color
    return color


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = normalize_hex_color(color)[1:]
    if len(color) != 6:
        raise ValueError(f"非法 16 进制颜色: #{color}")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )

def parse_line_name(td: html.HtmlElement) -> str:
    # 优先取链接文字，例如 “北京1号线”
    links = td.xpath(".//a")
    if links:
        text = links[0].text_content().strip()
        if text:
            return text

    # 回退：取整个单元格文本，并清理掉前面的色块字符
    text = td.text_content().strip()
    text = text.replace("█", "").strip()
    return text

def parse_hex_color(td: html.HtmlElement):
    text = td.text_content().strip().upper()
    
    if len(text) < 6:
        return None
    return text

def parse_table(table: html.HtmlElement) -> list[Metro]:
    result: list[Metro] = []
    current_district: str | None = None

    for tr in table.xpath(".//tr"):
        tds = tr.xpath("./td")

        if not tds:
            continue

        # 只要遇到横跨三列的标题行，就更新当前地区名
        # 不判断它是“华北地区”还是“北京市”
        if len(tds) == 1 and tds[0].get("colspan") == "3":
            current_district = tds[0].text_content().strip()
            continue

        # 真正的数据行：三个 td
        if len(tds) == 3:
            if not current_district:
                continue

            line_name = parse_line_name(tds[0])
            hex_color = parse_hex_color(tds[1])
            rgb_color = parse_rgb(tds[2].text_content().strip())
            if hex_color and rgb_color and current_district not in ['通长图', 'G总的图', '图标', '未知']:
                result.append(
                    Metro(
                        district=current_district,
                        lineName=line_name,
                        hexColor=hex_color,
                        rgbColor=rgb_color,
                    )
                )

    return result

def color_distance2(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    dr = a[0] - b[0]
    dg = a[1] - b[1]
    db = a[2] - b[2]
    return dr * dr + dg * dg + db * db


def build_district_metros(metros: list[Metro]) -> dict[str, list[Metro]]:
    district_map: dict[str, list[Metro]] = defaultdict(list)
    for metro in metros:
        district_map[metro.district].append(metro)
    return dict(district_map)


def guess_district(colors: list[str], metros: list[Metro]) -> str | None:
    """
    根据给定颜色组合猜测所属城市。
    允许输入颜色与标准颜色有细微差异。

    算法：
    - 对每个城市
    - 对每个输入颜色，找到该城市中颜色差异最小的一条线路
    - 把这些最小差异累加，得到总分
    - 返回总分最小的城市
    """
    if not colors:
        return None

    input_rgbs = [hex_to_rgb(c) for c in colors if c.strip()]
    if not input_rgbs:
        return None

    district_map = build_district_metros(metros)

    best_district: str | None = None
    best_score: int | None = None
    ranked_district = {}
    for district, district_metros in district_map.items():
        if not district_metros:
            continue

        total_score = 0
        lines = []
        for input_rgb in input_rgbs:
            score_list = [(color_distance2(input_rgb, metro.rgbColor), metro.lineName) for metro in district_metros]
            score_list.sort(key=lambda x: x[0])
            total_score += score_list[0][0]
            lines.append(score_list[0][1])
        if best_score is None or total_score < best_score:
            best_score = total_score
            best_district = district
        ranked_district[district] = (total_score, lines)
    ranked_district = dict(sorted(ranked_district.items(), key=lambda x: x[1]))
    return best_district, ranked_district

def guess_district_scores(colors: list[str], metros: list[Metro]) -> list[tuple[str, int]]:
    """
    返回所有城市的匹配得分，分数越小越接近。
    """
    if not colors:
        return []

    input_rgbs = [hex_to_rgb(c) for c in colors if c.strip()]
    if not input_rgbs:
        return []

    district_map = build_district_metros(metros)
    scores: list[tuple[str, int]] = []

    for district, district_metros in district_map.items():
        if not district_metros:
            continue

        total_score = 0
        for input_rgb in input_rgbs:
            min_dist = min(
                color_distance2(input_rgb, metro.rgbColor)
                for metro in district_metros
            )
            total_score += min_dist

        scores.append((district, total_score))

    scores.sort(key=lambda x: x[1])
    return scores

def test():
    testcases = [
        (["#feb500", "#b20001", "#25ac7f"], '哈尔滨市'),
        (["#E9AE00", "#EB7835", "#30895F"], '成都市'),
    ]
    for ind, testcase in enumerate(testcases):
        best, candidates = guess_district(testcase[0], metros)
        print(f'第{ind+1}个测试：{" / ".join(testcase[0])}')
        print(f'测试{"不" if best != testcase[1] else ""}通过：标准答案【{testcase[1]}】，计算最佳答案【{best}】，对应线路{" / ".join(candidates[best][1])}。')
        # print(f'其余候选答案：{"、".join(candidates.keys())}')
        print('========================================')

if __name__ == '__main__':
    cache = Path(__file__).parent / "metro-colors.html"
    if not cache.is_file():
        print(
            f"请使用浏览器打开https://zhrail.huijiwiki.com/wiki/%E6%A0%87%E5%BF%97%E8%89%B2%E4%B8%80%E8%A7%88 ctrl+S保存到 {cache.as_posix()} 后再重新运行本脚本"
        )
        exit(0)

    with open(cache, "r", encoding="utf8") as f:
        source = html.parse(f)

    tables = source.xpath('//*[@id="mw-content-text"]//table[@class="wikitable"]')

    metros: list[Metro] = []
    for table in tables:
        metros.extend(parse_table(table))
    
    # 测试
    # test()
    for testcase in [
        ['#ff5d5d','#3eb1ff'],
        ['#f44336','#ffb000','#3b8b5a'],
        ['#1aa043','#2c6fdb','#ffcc00','#ff1f1f'],
        ['#c14cc5','#2fb8f4','#f44242','#35bc4e'],
        ['#2ca84f','#9966cc','#3366cc','#c4cc23','#ff3333'],
        ['#36ba55','#ff9900','#d663c9','#27c1b9','#2b7ee0','#ff0101'],
        ['#ffa329','#f456a6','#ea2f2f','#2730a0','#008bd8','#875d32','#a2c60a']
    ]:
        best, candidates = guess_district(testcase, metros)
        print(f'最佳匹配：{best}，对应线路{" / ".join(candidates[best][1])}')