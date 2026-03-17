"""
utils/validators.py - 输入验证模块

提供金额、日期、类别合法性、ID存在等验证功能。
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from utils.config import ALLOWED_CATEGORIES, DATE_FORMAT, MAX_DESCRIPTION_LENGTH, MIN_AMOUNT


def validate_amount(amount_str: str) -> Optional[float]:
    """
    验证金额是否为有效的正浮点数。
    
    Args:
        amount_str: 金额字符串
        
    Returns:
        验证通过返回浮点数，否则返回 None
    """
    try:
        amount = float(amount_str)
        if amount <= MIN_AMOUNT:
            print(f"错误：金额必须大于 {MIN_AMOUNT}")
            return None
        return round(amount, 2)
    except ValueError:
        print("错误：金额必须是有效的数字")
        return None


def validate_category(category: str) -> bool:
    """
    验证类别是否在允许列表中。
    
    Args:
        category: 类别字符串
        
    Returns:
        验证通过返回 True，否则返回 False
    """
    if category in ALLOWED_CATEGORIES:
        return True
    print(f"错误：类别必须是以下之一：{', '.join(ALLOWED_CATEGORIES)}")
    return False


def validate_date(date_str: str) -> Optional[str]:
    """
    验证日期格式是否为有效的 YYYY-MM-DD。
    
    Args:
        date_str: 日期字符串
        
    Returns:
        验证通过返回日期字符串，否则返回 None
    """
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(date_str):
        print("错误：日期格式必须为 YYYY-MM-DD")
        return None
    
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return date_str
    except ValueError:
        print("错误：无效的日期")
        return None


def validate_description(description: str) -> bool:
    """
    验证描述长度是否超过限制。
    
    Args:
        description: 描述字符串
        
    Returns:
        验证通过返回 True，否则返回 False
    """
    if len(description) <= MAX_DESCRIPTION_LENGTH:
        return True
    print(f"错误：描述不能超过 {MAX_DESCRIPTION_LENGTH} 个字符")
    return False


def validate_id_exists(expense_id: int, expenses: List[Dict[str, Any]]) -> bool:
    """
    验证ID是否存在于支出列表中。
    
    Args:
        expense_id: 支出ID
        expenses: 支出列表
        
    Returns:
        存在返回 True，否则返回 False
    """
    for expense in expenses:
        if expense.get("id") == expense_id:
            return True
    print(f"错误：ID {expense_id} 不存在")
    return False


def get_default_date() -> str:
    """
    获取今天的日期字符串。
    
    Returns:
        格式化的日期字符串
    """
    return datetime.now().strftime(DATE_FORMAT)


def parse_date_filter(date_str: str) -> Optional[str]:
    """
    解析日期过滤条件，支持 YYYY-MM-DD 或 YYYY-MM 格式。
    
    Args:
        date_str: 日期字符串
        
    Returns:
        验证通过返回日期字符串，否则返回 None
    """
    if not date_str:
        return None
    
    full_date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    month_pattern = re.compile(r"^\d{4}-\d{2}$")
    
    if full_date_pattern.match(date_str):
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return date_str
        except ValueError:
            print("错误：无效的日期")
            return None
    elif month_pattern.match(date_str):
        try:
            datetime.strptime(date_str + "-01", DATE_FORMAT)
            return date_str
        except ValueError:
            print("错误：无效的月份")
            return None
    else:
        print("错误：日期格式必须为 YYYY-MM-DD 或 YYYY-MM")
        return None
