"""CLI command implementations."""
import os
from datetime import datetime
from typing import Any

from core_expense import Expense
from data_manager import DataManager
from utils.util_validators import (
    validate_amount, validate_category, validate_date,
    validate_description, validate_id_exists
)
from utils.util_helpers import (
    filter_expenses, get_monthly_summary, get_yearly_summary,
    calculate_category_percentages, find_highest_lowest_days,
    generate_markdown_report
)
from utils.util_config import DEFAULT_DATE_FORMAT, OUTPUT_DIR


def cmd_add(args: Any, data_manager: DataManager) -> None:
    """Handle add command."""
    try:
        amount = getattr(args, 'amount', None)
        category = getattr(args, 'category', None)
        date_str = getattr(args, 'date', None)
        description = getattr(args, 'description', "")

        if date_str is None:
            date_str = datetime.now().strftime(DEFAULT_DATE_FORMAT)

        if not validate_amount(amount):
            print("错误：金额必须是大于0的数字")
            return
        if not validate_category(category):
            print("错误：类别必须是：餐饮、交通、购物、住房、水电、其他")
            return
        if not validate_date(date_str):
            print("错误：日期格式必须是YYYY-MM-DD")
            return
        if not validate_description(description):
            print("错误：描述不能超过100个字符")
            return

        exp_id = data_manager.get_next_id()
        expense = Expense(
            id=exp_id,
            amount=float(amount),
            category=category,
            date=date_str,
            description=description or ""
        )
        data_manager.add_expense(expense)
        print(f"成功添加支出: {expense}")
    except Exception as e:
        print(f"添加支出时出错")


def cmd_list(args: Any, data_manager: DataManager) -> None:
    """Handle list command."""
    try:
        expenses = data_manager.get_all_expenses()
        category = getattr(args, 'category', None)
        start_date = getattr(args, 'start_date', None)
        end_date = getattr(args, 'end_date', None)
        min_amt = getattr(args, 'min_amount', None)
        max_amt = getattr(args, 'max_amount', None)

        filtered = filter_expenses(
            expenses,
            category=category,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amt,
            max_amount=max_amt
        )

        if not filtered:
            print("没有找到符合条件的支出记录")
            return

        print(f"找到 {len(filtered)} 条记录:")
        print("-" * 60)
        for exp in filtered:
            print(exp)
    except Exception as e:
        print(f"查询支出时出错")


def cmd_summary(args: Any, data_manager: DataManager) -> None:
    """Handle summary command."""
    try:
        expenses = data_manager.get_all_expenses()
        period = getattr(args, 'period', 'month')
        year = getattr(args, 'year', None)
        month = getattr(args, 'month', None)

        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        if period == 'year':
            summary = get_yearly_summary(expenses, int(year))
            print(f"\n=== {year}年 支出统计 ===")
        else:
            summary = get_monthly_summary(expenses, int(year), int(month))
            print(f"\n=== {year}年{month}月 支出统计 ===")

        total = summary.get('total', 0.0)
        print(f"总支出: ¥{total:.2f}")

        percentages = calculate_category_percentages(summary.get('expenses', []))
        if percentages:
            print("\n各类别占比:")
            for cat, pct in sorted(percentages.items(), key=lambda x: x[1], reverse=True):
                amt = summary.get('category_totals', {}).get(cat, 0.0)
                print(f"  {cat}: ¥{amt:.2f} ({pct}%)")

        days_info = find_highest_lowest_days(summary.get('expenses', []))
        if days_info.get('highest'):
            highest = days_info['highest']
            print(f"\n最高支出日: {highest['date']} (¥{highest['amount']:.2f})")
        if days_info.get('lowest'):
            lowest = days_info['lowest']
            print(f"最低支出日: {lowest['date']} (¥{lowest['amount']:.2f})")
        print()
    except Exception as e:
        print(f"生成统计时出错")


def cmd_delete(args: Any, data_manager: DataManager) -> None:
    """Handle delete command."""
    try:
        expense_id = getattr(args, 'id', None)
        expenses = data_manager.get_all_expenses()

        if not validate_id_exists(expense_id, expenses):
            print(f"错误：ID {expense_id} 的支出记录不存在")
            return

        if data_manager.delete_expense(int(expense_id)):
            print(f"成功删除ID为 {expense_id} 的支出记录")
        else:
            print(f"删除失败")
    except Exception as e:
        print(f"删除支出时出错")


def cmd_export(args: Any, data_manager: DataManager) -> None:
    """Handle export command."""
    try:
        expenses = data_manager.get_all_expenses()
        period = getattr(args, 'period', 'month')
        year = getattr(args, 'year', None)
        month = getattr(args, 'month', None)

        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        year = int(year)
        month = int(month)

        if period == 'year':
            summary = get_yearly_summary(expenses, year)
            filename = f"{year}年支出报表.md"
        else:
            summary = get_monthly_summary(expenses, year, month)
            filename = f"{year}年{month:02d}月支出报表.md"

        markdown = generate_markdown_report(summary, period)
        filepath = os.path.join(OUTPUT_DIR, filename)

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"报表已导出到: {filepath}")
    except Exception as e:
        print(f"导出报表时出错")
