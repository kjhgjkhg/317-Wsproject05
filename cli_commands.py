"""
CLI Commands module for Expense Tracker.

Implements all subcommand handlers for the expense tracker CLI.
Each function corresponds to one subcommand (add, list, summary, delete, export).
"""

from datetime import datetime
from typing import Optional

from core_expense import Expense
from data_manager import DataManager
from utils.config import DATE_FORMAT, ALLOWED_CATEGORIES
from utils.validators import validate_expense_id
from utils.helpers import (
    calculate_total_amount,
    calculate_category_totals,
    calculate_category_percentages,
    find_max_expense_day,
    find_min_expense_day,
    sort_expenses,
    filter_expenses,
    save_markdown_report,
)


def cmd_add(
    data_manager: DataManager,
    amount: str,
    category: str,
    date: Optional[str] = None,
    description: str = "",
) -> int:
    """
    Handle the 'add' subcommand.

    Args:
        data_manager: The DataManager instance.
        amount: Amount as string.
        category: Expense category.
        date: Date string (defaults to today).
        description: Optional description.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Use today's date if not provided
    if date is None:
        date = datetime.now().strftime(DATE_FORMAT)

    # Get next ID
    next_id = data_manager.get_next_id()

    # Create expense with validation
    success, result = Expense.create_new(
        next_id=next_id,
        amount_str=amount,
        category=category,
        date_str=date,
        description=description,
    )

    if not success:
        print(f"错误: {result}")
        return 1

    expense = result

    # Add to database
    success, error = data_manager.add_expense(expense)
    if not success:
        print(f"错误: {error}")
        return 1

    print(f"成功添加支出记录:")
    print(f"  ID: {expense.id}")
    print(f"  金额: ¥{expense.amount:.2f}")
    print(f"  类别: {expense.category}")
    print(f"  日期: {expense.date}")
    print(f"  描述: {expense.description}")

    return 0


def cmd_list(
    data_manager: DataManager,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_by: str = "date",
    reverse: bool = False,
) -> int:
    """
    Handle the 'list' subcommand.

    Args:
        data_manager: The DataManager instance.
        category: Filter by category.
        start_date: Filter by start date.
        end_date: Filter by end date.
        min_amount: Filter by minimum amount.
        max_amount: Filter by maximum amount.
        sort_by: Sort field (date, amount, category).
        reverse: Sort in descending order.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    expenses = data_manager.get_all_expenses()

    if not expenses:
        print("暂无支出记录")
        return 0

    # Apply filters
    filtered = filter_expenses(
        expenses,
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    if not filtered:
        print("没有符合条件的支出记录")
        return 0

    # Sort results
    sorted_expenses = sort_expenses(filtered, sort_by=sort_by, reverse=reverse)

    # Display header
    print(f"\n{'ID':<6} {'日期':<12} {'类别':<8} {'金额':>10} {'描述'}")
    print("-" * 70)

    # Display records
    total = 0.0
    for expense in sorted_expenses:
        expense_id = expense.get("id", "-")
        date = expense.get("date", "-")
        cat = expense.get("category", "-")
        amount = expense.get("amount", 0.0)
        desc = expense.get("description", "")[:25]

        print(f"{expense_id:<6} {date:<12} {cat:<8} ¥{amount:>8.2f} {desc}")
        total += amount

    print("-" * 70)
    print(f"{'合计':<28} ¥{total:>8.2f} ({len(sorted_expenses)} 条记录)")
    print()

    return 0


def cmd_summary(
    data_manager: DataManager,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> int:
    """
    Handle the 'summary' subcommand.

    Args:
        data_manager: The DataManager instance.
        year: Filter by year (defaults to current year).
        month: Filter by month (optional).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Default to current year
    if year is None:
        year = datetime.now().year

    expenses = data_manager.get_all_expenses()

    # Filter by year
    year_str = str(year)
    filtered = [e for e in expenses if e.get("date", "").startswith(year_str)]

    # Filter by month if specified
    if month is not None:
        month_prefix = f"{year}-{month:02d}"
        filtered = [e for e in filtered if e.get("date", "").startswith(month_prefix)]

    if not filtered:
        period = f"{year}年" if month is None else f"{year}年{month}月"
        print(f"{period}暂无支出记录")
        return 0

    # Calculate statistics
    total = calculate_total_amount(filtered)
    category_totals = calculate_category_totals(filtered)
    category_percentages = calculate_category_percentages(filtered)
    max_day, max_amount = find_max_expense_day(filtered)
    min_day, min_amount = find_min_expense_day(filtered)

    # Display summary
    period = f"{year}年" if month is None else f"{year}年{month:02d}月"
    print(f"\n{'='*50}")
    print(f"  {period} 支出汇总")
    print(f"{'='*50}")

    print(f"\n总支出: ¥{total:.2f}")
    print(f"记录数: {len(filtered)} 条")

    print(f"\n{'分类统计':-^46}")
    print(f"{'类别':<10} {'金额':>12} {'占比':>10} {'条形图'}")
    print("-" * 46)

    for cat in ALLOWED_CATEGORIES:
        amount = category_totals.get(cat, 0.0)
        pct = category_percentages.get(cat, 0.0)
        bar = "█" * int(pct / 5)  # 20 chars max
        print(f"{cat:<10} ¥{amount:>10.2f} {pct:>9.1f}% {bar}")

    print(f"\n{'支出极值':-^46}")
    if max_day:
        print(f"最高支出日: {max_day} (¥{max_amount:.2f})")
    if min_day:
        print(f"最低支出日: {min_day} (¥{min_amount:.2f})")

    print(f"\n{'='*50}\n")

    return 0


def cmd_delete(data_manager: DataManager, expense_id: str) -> int:
    """
    Handle the 'delete' subcommand.

    Args:
        data_manager: The DataManager instance.
        expense_id: ID of the expense to delete (as string).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Get valid IDs
    existing_ids = data_manager.get_all_ids()

    # Validate ID
    is_valid, parsed_id, error = validate_expense_id(expense_id, existing_ids)
    if not is_valid:
        print(f"错误: {error}")
        return 1

    # Get expense details before deletion for confirmation
    expense = data_manager.get_expense_by_id(parsed_id)
    if expense:
        print("将要删除以下记录:")
        print(f"  ID: {expense['id']}")
        print(f"  金额: ¥{expense['amount']:.2f}")
        print(f"  类别: {expense['category']}")
        print(f"  日期: {expense['date']}")
        print(f"  描述: {expense['description']}")

    # Delete from database
    success, error = data_manager.delete_expense(parsed_id)
    if not success:
        print(f"错误: {error}")
        return 1

    print(f"成功删除支出记录 (ID: {parsed_id})")
    return 0


def cmd_export(
    data_manager: DataManager,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> int:
    """
    Handle the 'export' subcommand.

    Args:
        data_manager: The DataManager instance.
        year: Export year (defaults to current year).
        month: Export month (defaults to current month).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Default to current year and month
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    expenses = data_manager.get_all_expenses()

    # Filter by year and month
    month_prefix = f"{year}-{month:02d}"
    filtered = [e for e in expenses if e.get("date", "").startswith(month_prefix)]

    if not filtered:
        print(f"{year}年{month:02d}月暂无支出记录，无法导出")
        return 1

    # Generate and save report
    success, result = save_markdown_report(filtered, year, month)

    if not success:
        print(f"错误: 导出失败 - {result}")
        return 1

    print(f"成功导出报表到: {result}")
    print(f"  包含 {len(filtered)} 条记录")
    print(f"  总金额: ¥{calculate_total_amount(filtered):.2f}")

    return 0
