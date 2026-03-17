"""Helper functions for statistics and Markdown generation."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from utils.util_config import DEFAULT_DATE_FORMAT


def filter_expenses(expenses: List, category: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    min_amount: Optional[float] = None,
                    max_amount: Optional[float] = None) -> List:
    """Filter expenses by various criteria."""
    result = expenses[:]
    try:
        if category:
            result = [e for e in result if hasattr(e, 'category') and e.category == category]
        if start_date:
            result = [e for e in result if hasattr(e, 'date') and e.date >= start_date]
        if end_date:
            result = [e for e in result if hasattr(e, 'date') and e.date <= end_date]
        if min_amount is not None:
            result = [e for e in result if hasattr(e, 'amount') and e.amount >= min_amount]
        if max_amount is not None:
            result = [e for e in result if hasattr(e, 'amount') and e.amount <= max_amount]
    except Exception:
        pass
    return result


def get_monthly_summary(expenses: List, year: int, month: int) -> Dict[str, Any]:
    """Get summary for a specific month."""
    result: Dict[str, Any] = {"total": 0.0, "expenses": [], "category_totals": defaultdict(float)}
    try:
        target_start = f"{year:04d}-{month:02d}-01"
        target_end = f"{year:04d}-{month:02d}-31"
        filtered = filter_expenses(expenses, start_date=target_start, end_date=target_end)
        result["expenses"] = filtered
        for exp in filtered:
            if hasattr(exp, 'amount') and hasattr(exp, 'category'):
                result["total"] += exp.amount
                result["category_totals"][exp.category] += exp.amount
        result["category_totals"] = dict(result["category_totals"])
    except Exception:
        pass
    return result


def get_yearly_summary(expenses: List, year: int) -> Dict[str, Any]:
    """Get summary for a specific year."""
    result: Dict[str, Any] = {"total": 0.0, "expenses": [], "monthly_totals": defaultdict(float)}
    try:
        target_start = f"{year:04d}-01-01"
        target_end = f"{year:04d}-12-31"
        filtered = filter_expenses(expenses, start_date=target_start, end_date=target_end)
        result["expenses"] = filtered
        for exp in filtered:
            if hasattr(exp, 'amount'):
                result["total"] += exp.amount
            if hasattr(exp, 'date'):
                try:
                    date_obj = datetime.strptime(exp.date, DEFAULT_DATE_FORMAT)
                    month_key = f"{date_obj.month:02d}月"
                    result["monthly_totals"][month_key] += exp.amount
                except Exception:
                    pass
        result["monthly_totals"] = dict(result["monthly_totals"])
    except Exception:
        pass
    return result


def calculate_category_percentages(expenses: List) -> Dict[str, float]:
    """Calculate percentage for each category."""
    result: Dict[str, float] = {}
    try:
        category_totals: Dict[str, float] = defaultdict(float)
        total = 0.0
        for exp in expenses:
            if hasattr(exp, 'amount') and hasattr(exp, 'category'):
                category_totals[exp.category] += exp.amount
                total += exp.amount
        if total > 0:
            for cat, amt in category_totals.items():
                result[cat] = round((amt / total) * 100, 2)
    except Exception:
        pass
    return result


def find_highest_lowest_days(expenses: List) -> Dict[str, Any]:
    """Find days with highest and lowest expenses."""
    result: Dict[str, Any] = {"highest": {"date": "", "amount": 0.0},
                              "lowest": {"date": "", "amount": float('inf')}}
    try:
        daily_totals: Dict[str, float] = defaultdict(float)
        for exp in expenses:
            if hasattr(exp, 'date') and hasattr(exp, 'amount'):
                daily_totals[exp.date] += exp.amount
        if not daily_totals:
            return {"highest": None, "lowest": None}
        for date_str, amt in daily_totals.items():
            if amt > result["highest"]["amount"]:
                result["highest"] = {"date": date_str, "amount": amt}
            if amt < result["lowest"]["amount"]:
                result["lowest"] = {"date": date_str, "amount": amt}
        if result["lowest"]["amount"] == float('inf'):
            result["lowest"] = None
    except Exception:
        pass
    return result


def generate_markdown_report(summary_data: Dict[str, Any], report_type: str) -> str:
    """Generate Markdown report from summary data."""
    lines = []
    try:
        today = datetime.now().strftime(DEFAULT_DATE_FORMAT)
        title = "年度支出报表" if report_type == "yearly" else "月度支出报表"
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"生成日期: {today}")
        lines.append("")
        lines.append(f"## 总支出: ¥{summary_data.get('total', 0.0):.2f}")
        lines.append("")
        lines.append("### 类别统计")
        lines.append("")
        lines.append("| 类别 | 金额 | 占比 |")
        lines.append("|------|------|------|")
        category_totals = summary_data.get("category_totals", {})
        total = summary_data.get("total", 0.0)
        for cat, amt in sorted(category_totals.items()):
            pct = (amt / total * 100) if total > 0 else 0.0
            lines.append(f"| {cat} | ¥{amt:.2f} | {pct:.1f}% |")
        lines.append("")
        if report_type == "yearly":
            lines.append("### 月度趋势")
            lines.append("")
            lines.append("| 月份 | 金额 |")
            lines.append("|------|------|")
            monthly = summary_data.get("monthly_totals", {})
            for month_key in sorted(monthly.keys()):
                lines.append(f"| {month_key} | ¥{monthly[month_key]:.2f} |")
        lines.append("")
        lines.append("### 交易记录")
        lines.append("")
        lines.append("| ID | 日期 | 类别 | 金额 | 描述 |")
        lines.append("|----|------|------|------|------|")
        for exp in summary_data.get("expenses", []):
            if hasattr(exp, 'id') and hasattr(exp, 'date'):
                desc = exp.description[:20] if hasattr(exp, 'description') and exp.description else ""
                lines.append(f"| {exp.id} | {exp.date} | {exp.category} | ¥{exp.amount:.2f} | {desc} |")
    except Exception:
        pass
    return "\n".join(lines)
