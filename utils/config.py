"""
utils/config.py - 常量配置模块

定义文件路径、允许类别列表、默认日期格式等常量。
"""

import os
from typing import List

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_DATA_DIR: str = os.path.join(BASE_DIR, "source_data")
OUTPUT_BUILD_DIR: str = os.path.join(BASE_DIR, "output_build")

EXPENSES_FILE: str = os.path.join(SOURCE_DATA_DIR, "expenses.json")
CONFIG_FILE: str = os.path.join(SOURCE_DATA_DIR, ".do_not_touch.cfg")

ALLOWED_CATEGORIES: List[str] = [
    "餐饮",
    "交通",
    "购物",
    "住房",
    "水电",
    "其他"
]

DATE_FORMAT: str = "%Y-%m-%d"

MAX_DESCRIPTION_LENGTH: int = 100

MIN_AMOUNT: float = 0.0
