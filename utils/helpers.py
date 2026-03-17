"""
utils/helpers.py - 统计计算与报表生成模块

提供月度汇总、类别占比、排序计算和 Markdown 报表生成功能。
"""

from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

from utils.config import DATE_FORMAT, OUTPUT_BUILD_DIR, ALLOWED_CATEGORIES


def calculate_monthly_summary(
    expenses: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, Any]:
    """
    计算指定月份的支出汇总。
    
    Args:
        expenses: 支出列表
        year: 年份
        month: 月份
        
    Returns:
        包含汇总数据的字典
    """
    monthly_expenses = []
    for expense in expenses:
        try:
            expense_date = datetime.strptime(expense.get("date", ""), DATE_FORMAT)
            if expense_date.year == year and expense_date.month == month:
                monthly_expenses.append(expense)
        except (ValueError, TypeError):
            continue
    
    total_amount = 0.0
    category_totals: Dict[str, float] = defaultdict(float)
    daily_totals: Dict[str, float] = defaultdict(float)
    
    for expense in monthly_expenses:
        amount = expense.get("amount", 0.0)
        category = expense.get("category", "其他")
        date = expense.get("date", "")
        
        total_amount += amount
        category_totals[category] += amount
        daily_totals[date] += amount
    
    category_percentages: Dict[str, Tuple[float, float]] = {}
    for category, amount in category_totals.items():
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0.0
        category_percentages[category] = (amount, percentage)
    
    highest_day: Optional[str] = None
    lowest_day: Optional[str] = None
    highest_amount = 0.0
    lowest_amount = float("inf")
    
    for date, amount in daily_totals.items():
        if amount > highest_amount:
            highest_amount = amount
            highest_day = date
        if amount < lowest_amount:
            lowest_amount = amount
            lowest_day = date
    
    if lowest_amount == float("inf"):
        lowest_amount = 0.0
    
    return {
        "year": year,
        "month": month,
        "total_amount": round(total_amount, 2),
        "category_totals": dict(category_totals),
        "category_percentages": category_percentages,
        "expense_count": len(monthly_expenses),
        "highest_day": highest_day,
        "highest_amount": round(highest_amount, 2),
        "lowest_day": lowest_day,
        "lowest_amount": round(lowest_amount, 2),
        "daily_totals": dict(daily_totals)
    }


def calculate_yearly_summary(
    expenses: List[Dict[str, Any]], year: int
) -> Dict[str, Any]:
    """
    计算指定年份的支出汇总。
    
    Args:
        expenses: 支出列表
        year: 年份
        
    Returns:
        包含汇总数据的字典
    """
    yearly_expenses = []
    for expense in expenses:
        try:
            expense_date = datetime.strptime(expense.get("date", ""), DATE_FORMAT)
            if expense_date.year == year:
                yearly_expenses.append(expense)
        except (ValueError, TypeError):
            continue
    
    total_amount = 0.0
    category_totals: Dict[str, float] = defaultdict(float)
    monthly_totals: Dict[int, float] = defaultdict(float)
    
    for expense in yearly_expenses:
        amount = expense.get("amount", 0.0)
        category = expense.get("category", "其他")
        try:
            expense_date = datetime.strptime(expense.get("date", ""), DATE_FORMAT)
            monthly_totals[expense_date.month] += amount
        except (ValueError, TypeError):
            pass
        
        total_amount += amount
        category_totals[category] += amount
    
    category_percentages: Dict[str, Tuple[float, float]] = {}
    for category, amount in category_totals.items():
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0.0
        category_percentages[category] = (amount, percentage)
    
    highest_month: Optional[int] = None
    lowest_month: Optional[int] = None
    highest_amount = 0.0
    lowest_amount = float("inf")
    
    for month, amount in monthly_totals.items():
        if amount > highest_amount:
            highest_amount = amount
            highest_month = month
        if amount < lowest_amount:
            lowest_amount = amount
            lowest_month = month
    
    if lowest_amount == float("inf"):
        lowest_amount = 0.0
    
    return {
        "year": year,
        "total_amount": round(total_amount, 2),
        "category_totals": dict(category_totals),
        "category_percentages": category_percentages,
        "expense_count": len(yearly_expenses),
        "monthly_totals": dict(monthly_totals),
        "highest_month": highest_month,
        "highest_amount": round(highest_amount, 2),
        "lowest_month": lowest_month,
        "lowest_amount": round(lowest_amount, 2)
    }


def generate_monthly_markdown(summary: Dict[str, Any]) -> str:
    """
    生成月度报表的 Markdown 文本。
    
    Args:
        summary: 月度汇总数据
        
    Returns:
        Markdown 格式的报表文本
    """
    lines = []
    lines.append(f"# {summary['year']}年{summary['month']}月支出报表")
    lines.append("")
    lines.append("## 概览")
    lines.append("")
    lines.append(f"- **总支出**: ¥{summary['total_amount']:.2f}")
    lines.append(f"- **记录数**: {summary['expense_count']} 笔")
    lines.append(f"- **最高支出日**: {summary['highest_day'] or '无'} (¥{summary['highest_amount']:.2f})")
    lines.append(f"- **最低支出日**: {summary['lowest_day'] or '无'} (¥{summary['lowest_amount']:.2f})")
    lines.append("")
    lines.append("## 类别统计")
    lines.append("")
    lines.append("| 类别 | 金额 | 占比 |")
    lines.append("|:---:|:---:|:---:|")
    
    sorted_categories = sorted(
        summary["category_percentages"].items(),
        key=lambda x: x[1][0],
        reverse=True
    )
    
    for category, (amount, percentage) in sorted_categories:
        lines.append(f"| {category} | ¥{amount:.2f} | {percentage:.1f}% |")
    
    lines.append("")
    lines.append("## 每日支出")
    lines.append("")
    lines.append("| 日期 | 金额 |")
    lines.append("|:---:|:---:|")
    
    sorted_days = sorted(summary["daily_totals"].items())
    for date, amount in sorted_days:
        lines.append(f"| {date} | ¥{amount:.2f} |")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(lines)


def generate_yearly_markdown(summary: Dict[str, Any]) -> str:
    """
    生成年度报表的 Markdown 文本。
    
    Args:
        summary: 年度汇总数据
        
    Returns:
        Markdown 格式的报表文本
    """
    lines = []
    lines.append(f"# {summary['year']}年支出报表")
    lines.append("")
    lines.append("## 概览")
    lines.append("")
    lines.append(f"- **总支出**: ¥{summary['total_amount']:.2f}")
    lines.append(f"- **记录数**: {summary['expense_count']} 笔")
    lines.append(f"- **最高支出月**: {summary['highest_month']}月 (¥{summary['highest_amount']:.2f})" if summary['highest_month'] else "- **最高支出月**: 无")
    lines.append(f"- **最低支出月**: {summary['lowest_month']}月 (¥{summary['lowest_amount']:.2f})" if summary['lowest_month'] else "- **最低支出月**: 无")
    lines.append("")
    lines.append("## 类别统计")
    lines.append("")
    lines.append("| 类别 | 金额 | 占比 |")
    lines.append("|:---:|:---:|:---:|")
    
    sorted_categories = sorted(
        summary["category_percentages"].items(),
        key=lambda x: x[1][0],
        reverse=True
    )
    
    for category, (amount, percentage) in sorted_categories:
        lines.append(f"| {category} | ¥{amount:.2f} | {percentage:.1f}% |")
    
    lines.append("")
    lines.append("## 月度统计")
    lines.append("")
    lines.append("| 月份 | 金额 |")
    lines.append("|:---:|:---:|")
    
    for month in range(1, 13):
        amount = summary["monthly_totals"].get(month, 0.0)
        lines.append(f"| {month}月 | ¥{amount:.2f} |")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    return "\n".join(lines)


def save_markdown_report(content: str, filename: str) -> bool:
    """
    保存 Markdown 报表到文件。
    
    Args:
        content: Markdown 内容
        filename: 文件名
        
    Returns:
        成功返回 True，失败返回 False
    """
    import os
    
    try:
        if not os.path.exists(OUTPUT_BUILD_DIR):
            os.makedirs(OUTPUT_BUILD_DIR)
        
        filepath = os.path.join(OUTPUT_BUILD_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"错误：保存报表失败 - {e}")
        return False


def sort_expenses(
    expenses: List[Dict[str, Any]],
    sort_by: str = "date",
    reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    对支出列表进行排序。
    
    Args:
        expenses: 支出列表
        sort_by: 排序字段 (date/amount/category)
        reverse: 是否降序
        
    Returns:
        排序后的列表
    """
    valid_sort_fields = ["date", "amount", "category"]
    if sort_by not in valid_sort_fields:
        sort_by = "date"
    
    def sort_key(expense: Dict[str, Any]) -> Any:
        if sort_by == "date":
            return expense.get("date", "")
        elif sort_by == "amount":
            return expense.get("amount", 0.0)
        elif sort_by == "category":
            return expense.get("category", "")
        return ""
    
    return sorted(expenses, key=sort_key, reverse=reverse)
