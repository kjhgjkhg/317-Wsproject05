"""
Configuration module for Expense Tracker.

Contains all constants, file paths, and allowed values.
This module should not import any other project modules to avoid circular imports.
"""

import os
from typing import List


# =============================================================================
# DIRECTORY PATHS (STRICT CONSTRAINTS)
# =============================================================================

# Data directory - ONLY for reading/writing expenses.json
DATA_DIR: str = "./source_data"

# Output directory - ONLY for exporting Markdown reports
OUTPUT_DIR: str = "./output_build"

# Data file path (the ONLY file allowed to be modified in DATA_DIR)
EXPENSES_FILE_PATH: str = os.path.join(DATA_DIR, "expenses.json")

# Protected file that must not be touched
PROTECTED_FILE: str = os.path.join(DATA_DIR, ".do_not_touch.cfg")


# =============================================================================
# EXPENSE CATEGORIES (STRICT WHITELIST)
# =============================================================================

ALLOWED_CATEGORIES: List[str] = [
    "餐饮",
    "交通",
    "购物",
    "住房",
    "水电",
    "其他",
]


# =============================================================================
# DATE FORMATS
# =============================================================================

DATE_FORMAT: str = "%Y-%m-%d"
DATE_FORMAT_DISPLAY: str = "YYYY-MM-DD"
DATE_FORMAT_HELP: str = "YYYY-MM-DD"


# =============================================================================
# VALIDATION CONSTRAINTS
# =============================================================================

# Amount must be greater than this value
MIN_AMOUNT: float = 0.0

# Maximum description length
MAX_DESCRIPTION_LENGTH: int = 100


# =============================================================================
# EXPORT SETTINGS
# =============================================================================

# Markdown report filename template
# {year} and {month} will be replaced with actual values
REPORT_FILENAME_TEMPLATE: str = "expense_report_{year}_{month:02d}.md"


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES = {
    "invalid_amount": f"金额必须大于 {MIN_AMOUNT}",
    "invalid_category": f"类别必须是以下之一: {', '.join(ALLOWED_CATEGORIES)}",
    "invalid_date": f"日期格式无效，请使用 {DATE_FORMAT_DISPLAY} 格式",
    "invalid_description": f"描述不能超过 {MAX_DESCRIPTION_LENGTH} 个字符",
    "expense_not_found": "找不到指定ID的支出记录",
    "file_access_error": "文件访问错误",
    "json_parse_error": "JSON解析错误",
    "permission_denied": "权限不足，无法访问文件",
}
