"""Input validation module for expense tracker."""
from datetime import datetime
from typing import List, Any

from utils.util_config import ALLOWED_CATEGORIES, DEFAULT_DATE_FORMAT, MAX_DESCRIPTION_LENGTH


def validate_amount(amount: Any) -> bool:
    """Validate amount is a positive float."""
    try:
        amount_val = float(amount)
        return amount_val > 0
    except (ValueError, TypeError):
        return False


def validate_category(category: str) -> bool:
    """Validate category is in allowed list."""
    return category in ALLOWED_CATEGORIES


def validate_date(date_str: str) -> bool:
    """Validate date string is valid YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, DEFAULT_DATE_FORMAT)
        return True
    except (ValueError, TypeError):
        return False


def validate_description(description: str) -> bool:
    """Validate description length."""
    if description is None:
        return True
    try:
        return len(str(description)) <= MAX_DESCRIPTION_LENGTH
    except Exception:
        return False


def validate_id_exists(expense_id: int, expenses: List) -> bool:
    """Validate expense ID exists in the list."""
    try:
        expense_id_int = int(expense_id)
        for exp in expenses:
            if hasattr(exp, 'id') and exp.id == expense_id_int:
                return True
        return False
    except (ValueError, TypeError):
        return False
