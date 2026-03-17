"""Configuration module for expense tracker."""
import os
from typing import List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "source_data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_build")
DATA_FILE = os.path.join(DATA_DIR, "expenses.json")

ALLOWED_CATEGORIES: List[str] = ["餐饮", "交通", "购物", "住房", "水电", "其他"]
DEFAULT_DATE_FORMAT: str = "%Y-%m-%d"
MAX_DESCRIPTION_LENGTH: int = 100
DO_NOT_TOUCH_FILE: str = os.path.join(DATA_DIR, ".do_not_touch.cfg")


def ensure_directories() -> None:
    """Ensure required directories exist."""
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
    except Exception:
        pass
