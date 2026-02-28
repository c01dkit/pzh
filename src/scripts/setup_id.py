import yaml
import secrets
import sys
import argparse
from pathlib import Path
from log import get_logger

known_hash = set()
def generate_id() -> str:
    """生成 16 位小写随机哈希值"""
    global known_hash
    random_id = secrets.token_hex(8)  # 8 字节 = 16 位十六进制字符
    while random_id in known_hash:
        random_id = secrets.token_hex(8)
    known_hash.add(random_id)
    return random_id


def add_id_recursive(data, overwrite: bool = False):
    """
    递归地为每个字典元素添加 id 字段。
    :param data:      YAML 解析后的数据结构
    :param overwrite: 是否覆盖已存在的 id 字段
    """
    global known_hash
    cnt = 0
    if isinstance(data, list):
        for item in data:
           cnt += add_id_recursive(item, overwrite)
    elif isinstance(data, dict):
        if "id" in data and len(data["id"]) == 16:
            known_hash.add(data["id"])
        if overwrite or "id" not in data or len(data["id"]) < 16:
            data["id"] = generate_id()
            cnt += 1
        for value in data.values():
            cnt += add_id_recursive(value, overwrite)
    return cnt

def main():
    parser = argparse.ArgumentParser(
        description="为 YAML 文件中每个字典元素添加随机 16 位小写 id 字段"
    )
    parser.add_argument("input", help="输入的 YAML 文件路径")
    parser.add_argument(
        "-o", "--output",
        help="输出的 YAML 文件路径（默认覆盖原文件）",
        default=None,
    )
    parser.add_argument(
        "--overwrite-id",
        action="store_true",
        help="强制覆盖已存在的 id 字段",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    if not input_path.exists():
        # print(f"[错误] 文件不存在: {input_path}")
        sys.exit(-1)

    # 读取 YAML
    with open(input_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        # print("[警告] YAML 文件为空，无需处理。")
        sys.exit(-1)

    # 添加 id 字段
    cnt = add_id_recursive(data, overwrite=args.overwrite_id)

    # 写出结果
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,   # 保持原有字段顺序
        )

    # print(f"[完成] 结果已写入: {output_path}")
    return cnt
"""
# 安装依赖（如未安装）
pip install pyyaml

# 原地修改文件
python setup-id.py data.yml

# 输出到新文件（保留原文件）
python setup-id.py data.yml -o output.yml

# 强制覆盖已存在的 id 字段
python setup-id.py data.yml --overwrite-id

"""

if __name__ == "__main__":
    logger = get_logger(__name__)
    cnt = main()
    logger.debug(f"{cnt} IDs generated.")
