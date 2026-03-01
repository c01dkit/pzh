import yaml
import secrets
import sys
import argparse
from pathlib import Path
from .log import get_logger

known_hash = set()
def generate_id() -> str:
    """生成 16 位小写随机哈希值"""
    global known_hash
    random_id = secrets.token_hex(8)  # 8 字节 = 16 位十六进制字符
    while random_id in known_hash:
        random_id = secrets.token_hex(8)
    known_hash.add(random_id)
    return random_id


def add_id_recursive(data, overwrite: bool = False, current_depth = 0, max_depth = 1):
    """
    递归地为每个字典元素添加 id 字段。
    :param data:      YAML 解析后的数据结构
    :param overwrite: 是否覆盖已存在的 id 字段
    """
    global known_hash
    cnt = 0
    if current_depth > max_depth:
        return 0
    if isinstance(data, list):
        for item in data:
           cnt += add_id_recursive(item, overwrite, current_depth+1)
    elif isinstance(data, dict):
        if "id" in data and isinstance(data["id"], str) and len(data["id"]) == 16:
            known_hash.add(data["id"])
        if overwrite or "id" not in data or data["id"] is None or len(data["id"]) < 16:
            data["id"] = generate_id()
            cnt += 1
        for value in data.values():
            cnt += add_id_recursive(value, overwrite, current_depth+1)
    return cnt

logger = get_logger(__name__)

def main(input_file:Path, output_file:Path=None, overwrite=False):
    
    input_path = Path(input_file)
    output_path = Path(output_file) if output_file else input_path
    if not input_path.exists():
        logger.error(f"文件不存在： {input_path}")
        return
    # 读取 YAML
    with open(input_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        logger.warning("YAML 文件为空，无需处理。")
        return 

    # 添加 id 字段
    cnt = add_id_recursive(data, overwrite=overwrite)

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
    logger.debug(f"为{output_path.name}生成了{cnt}个新的ID，当前缓存{len(known_hash)}个ID。")

    return 
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

