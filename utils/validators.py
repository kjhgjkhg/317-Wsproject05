"""
Input validation module for Expense Tracker.

Provides functions to validate all user inputs including amounts,
categories, dates, descriptions, and expense IDs.
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from utils.config import (
    ALLOWED_CATEGORIES,
    DATE_FORMAT,
    MAX_DESCRIPTION_LENGTH,
    MIN_AMOUNT,
    ERROR_MESSAGES,
)


def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validate that the amount is a positive float.

    Args:
        amount_str: String representation of the amount.

    Returns:
        Tuple of (is_valid, parsed_amount, error_message).
        If valid, parsed_amount contains the float value and error_message is empty.
    """
    try:
        amount = float(amount_str)
        if amount <= MIN_AMOUNT:
            return False, None, ERROR_MESSAGES["invalid_amount"]
        return True, amount, ""
    except ValueError:
        return False, None, ERROR_MESSAGES["invalid_amount"]


def validate_category(category: str) -> Tuple[bool, str]:
    """
    Validate that the category is in the allowed list.

    Args:
        category: The category string to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if category not in ALLOWED_CATEGORIES:
        return False, ERROR_MESSAGES["invalid_category"]
    return True, ""


def validate_date(date_str: str) -> Tuple[bool, Optional[datetime], str]:
    """
    Validate that the date string is in YYYY-MM-DD format.

    Args:
        date_str: Date string to validate.

    Returns:
        Tuple of (is_valid, parsed_date, error_message).
        If valid, parsed_date contains the datetime object.
    """
    try:
        parsed_date = datetime.strptime(date_str, DATE_FORMAT)
        return True, parsed_date, ""
    except ValueError:
        return False, None, ERROR_MESSAGES["invalid_date"]


def validate_description(description: str) -> Tuple[bool, str]:
    """
    Validate that the description does not exceed max length.

    Args:
        description: The description string to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, ERROR_MESSAGES["invalid_description"]
    return True, ""


def validate_expense_id(expense_id_str: str, existing_ids: List[int]) -> Tuple[bool, Optional[int], str]:
    """
    Validate that the expense ID exists in the database.

    Args:
        expense_id_str: String representation of the ID.
        existing_ids: List of valid expense IDs.

    Returns:
        Tuple of (is_valid, parsed_id, error_message).
    """
    try:
        expense_id = int(expense_id_str)
        if expense_id not in existing_ids:
            return False, None, ERROR_MESSAGES["expense_not_found"]
        return True, expense_id, ""
    except ValueError:
        return False, None, ERROR_MESSAGES["expense_not_found"]


def validate_all_inputs(
    amount_str: str,
    category: str,
    date_str: str,
    description: str,
) -> Tuple[bool, dict, str]:
    """
    Validate all expense input fields at once.

    Args:
        amount_str: Amount as string.
        category: Category string.
        date_str: Date string.
        description: Description string.

    Returns:
        Tuple of (all_valid, parsed_values, combined_error_message).
        parsed_values contains keys: amount, date.
    """
    errors = []
    parsed_values = {}

    # Validate amount
    is_valid, amount, error = validate_amount(amount_str)
    if not is_valid:
        errors.append(f"金额: {error}")
    else:
        parsed_values["amount"] = amount

    # Validate category
    is_valid, error = validate_category(category)
    if not is_valid:
        errors.append(f"类别: {error}")

    # Validate date
    is_valid, date_obj, error = validate_date(date_str)
    if not is_valid:
        errors.append(f"日期: {error}")
    else:
        parsed_values["date"] = date_obj

    # Validate description
    is_valid, error = validate_description(description)
    if not is_valid:
        errors.append(f"描述: {error}")

    if errors:
        return False, parsed_values, "; ".join(errors)
    return True, parsed_values, ""
