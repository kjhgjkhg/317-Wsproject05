"""
Helper utilities for Expense Tracker.

Provides statistical calculations, sorting, and Markdown report generation.
All calculations are implemented manually without external libraries.
"""

import os
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from utils.config import (
    ALLOWED_CATEGORIES,
    DATE_FORMAT,
    OUTPUT_DIR,
    REPORT_FILENAME_TEMPLATE,
)


def calculate_total_amount(expenses: List[Dict[str, Any]]) -> float:
    """
    Calculate the total amount of all expenses.

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Total amount as float.
    """
    total = 0.0
    for expense in expenses:
        total += expense.get("amount", 0.0)
    return total


def calculate_category_totals(expenses: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate total amount per category.

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Dictionary mapping category to total amount.
    """
    totals = defaultdict(float)
    for expense in expenses:
        category = expense.get("category", "其他")
        totals[category] += expense.get("amount", 0.0)
    return dict(totals)


def calculate_category_percentages(
    expenses: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Calculate percentage of total for each category.

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Dictionary mapping category to percentage (0-100).
    """
    total = calculate_total_amount(expenses)
    if total == 0:
        return {cat: 0.0 for cat in ALLOWED_CATEGORIES}

    category_totals = calculate_category_totals(expenses)
    percentages = {}
    for category in ALLOWED_CATEGORIES:
        amount = category_totals.get(category, 0.0)
        percentages[category] = round((amount / total) * 100, 2)
    return percentages


def find_max_expense_day(expenses: List[Dict[str, Any]]) -> Tuple[Optional[str], float]:
    """
    Find the day with the highest total expenses.

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Tuple of (date_string, total_amount). Returns (None, 0.0) if no expenses.
    """
    if not expenses:
        return None, 0.0

    daily_totals = defaultdict(float)
    for expense in expenses:
        date_str = expense.get("date", "")
        daily_totals[date_str] += expense.get("amount", 0.0)

    if not daily_totals:
        return None, 0.0

    max_date = max(daily_totals.keys(), key=lambda d: daily_totals[d])
    return max_date, daily_totals[max_date]


def find_min_expense_day(expenses: List[Dict[str, Any]]) -> Tuple[Optional[str], float]:
    """
    Find the day with the lowest total expenses (excluding days with 0 expenses).

    Args:
        expenses: List of expense dictionaries.

    Returns:
        Tuple of (date_string, total_amount). Returns (None, 0.0) if no expenses.
    """
    if not expenses:
        return None, 0.0

    daily_totals = defaultdict(float)
    for expense in expenses:
        date_str = expense.get("date", "")
        daily_totals[date_str] += expense.get("amount", 0.0)

    if not daily_totals:
        return None, 0.0

    min_date = min(daily_totals.keys(), key=lambda d: daily_totals[d])
    return min_date, daily_totals[min_date]


def sort_expenses(
    expenses: List[Dict[str, Any]],
    sort_by: str = "date",
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """
    Sort expenses by the specified field.

    Args:
        expenses: List of expense dictionaries.
        sort_by: Field to sort by ("date", "amount", "category").
        reverse: If True, sort in descending order.

    Returns:
        Sorted list of expenses.
    """
    def sort_key(expense: Dict[str, Any]):
        if sort_by == "date":
            date_str = expense.get("date", "")
            try:
                return datetime.strptime(date_str, DATE_FORMAT)
            except ValueError:
                return datetime.min
        elif sort_by == "amount":
            return expense.get("amount", 0.0)
        elif sort_by == "category":
            return expense.get("category", "")
        else:
            return expense.get("id", 0)

    return sorted(expenses, key=sort_key, reverse=reverse)


def filter_expenses(
    expenses: List[Dict[str, Any]],
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Filter expenses based on multiple criteria.

    Args:
        expenses: List of expense dictionaries.
        category: Filter by exact category match.
        start_date: Filter expenses on or after this date (YYYY-MM-DD).
        end_date: Filter expenses on or before this date (YYYY-MM-DD).
        min_amount: Filter expenses with amount >= this value.
        max_amount: Filter expenses with amount <= this value.

    Returns:
        Filtered list of expenses.
    """
    filtered = expenses.copy()

    if category:
        filtered = [e for e in filtered if e.get("category") == category]

    if start_date:
        filtered = [e for e in filtered if e.get("date", "") >= start_date]

    if end_date:
        filtered = [e for e in filtered if e.get("date", "") <= end_date]

    if min_amount is not None:
        filtered = [e for e in filtered if e.get("amount", 0.0) >= min_amount]

    if max_amount is not None:
        filtered = [e for e in filtered if e.get("amount", 0.0) <= max_amount]

    return filtered


def generate_markdown_report(
    expenses: List[Dict[str, Any]],
    year: int,
    month: int,
) -> str:
    """
    Generate a Markdown formatted expense report.

    Args:
        expenses: List of expense dictionaries for the period.
        year: Report year.
        month: Report month.

    Returns:
        Markdown formatted string.
    """
    lines = []

    # Title
    lines.append(f"# 支出报表 {year}年{month:02d}月")
    lines.append("")

    # Summary section
    total = calculate_total_amount(expenses)
    lines.append("## 汇总统计")
    lines.append("")
    lines.append(f"- **总支出**: ¥{total:.2f}")
    lines.append(f"- **记录数**: {len(expenses)} 条")
    lines.append("")

    # Category breakdown
    lines.append("## 分类统计")
    lines.append("")
    lines.append("| 类别 | 金额 | 占比 |")
    lines.append("|------|------|------|")

    category_totals = calculate_category_totals(expenses)
    category_percentages = calculate_category_percentages(expenses)

    for category in ALLOWED_CATEGORIES:
        amount = category_totals.get(category, 0.0)
        percentage = category_percentages.get(category, 0.0)
        lines.append(f"| {category} | ¥{amount:.2f} | {percentage}% |")

    lines.append("")

    # Daily extremes
    max_day, max_amount = find_max_expense_day(expenses)
    min_day, min_amount = find_min_expense_day(expenses)

    lines.append("## 支出极值")
    lines.append("")
    if max_day:
        lines.append(f"- **最高支出日**: {max_day} (¥{max_amount:.2f})")
    if min_day:
        lines.append(f"- **最低支出日**: {min_day} (¥{min_amount:.2f})")
    lines.append("")

    # Detailed records
    lines.append("## 详细记录")
    lines.append("")
    lines.append("| ID | 日期 | 类别 | 金额 | 描述 |")
    lines.append("|------|------|------|------|------|")

    sorted_expenses = sort_expenses(expenses, sort_by="date", reverse=True)
    for expense in sorted_expenses:
        lines.append(
            f"| {expense.get('id', '-')} | "
            f"{expense.get('date', '-')} | "
            f"{expense.get('category', '-')} | "
            f"¥{expense.get('amount', 0):.2f} | "
            f"{expense.get('description', '-')} |"
        )

    lines.append("")
    lines.append("---")
    lines.append(f"*报表生成时间: {datetime.now().strftime(DATE_FORMAT)}*")

    return "\n".join(lines)


def save_markdown_report(
    expenses: List[Dict[str, Any]],
    year: int,
    month: int,
) -> Tuple[bool, str]:
    """
    Generate and save a Markdown report to the output directory.

    Args:
        expenses: List of expense dictionaries.
        year: Report year.
        month: Report month.

    Returns:
        Tuple of (success, file_path or error_message).
    """
    try:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Generate report content
        content = generate_markdown_report(expenses, year, month)

        # Determine filename
        filename = REPORT_FILENAME_TEMPLATE.format(year=year, month=month)
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return True, filepath
    except Exception as e:
        return False, str(e)
