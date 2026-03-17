"""
cli_commands.py - CLI 子命令实现模块

实现所有子命令的具体逻辑：add/list/summary/delete/export。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from data_manager import DataManager
from utils.validators import (
    validate_amount,
    validate_category,
    validate_date,
    validate_description,
    validate_id_exists,
    get_default_date,
    parse_date_filter
)
from utils.helpers import (
    calculate_monthly_summary,
    calculate_yearly_summary,
    generate_monthly_markdown,
    generate_yearly_markdown,
    save_markdown_report,
    sort_expenses
)
from utils.config import ALLOWED_CATEGORIES, DATE_FORMAT


class CLICommands:
    """
    CLI 命令处理类，封装所有子命令的实现。
    """
    
    def __init__(self) -> None:
        """
        初始化命令处理器。
        """
        self.data_manager = DataManager()
    
    def add_expense(
        self,
        amount: str,
        category: str,
        date: Optional[str] = None,
        description: str = ""
    ) -> bool:
        """
        添加支出记录。
        
        Args:
            amount: 金额字符串
            category: 类别
            date: 日期字符串（可选，默认今天）
            description: 描述
            
        Returns:
            成功返回 True，失败返回 False
        """
        validated_amount = validate_amount(amount)
        if validated_amount is None:
            return False
        
        if not validate_category(category):
            return False
        
        if date is None:
            date = get_default_date()
        else:
            validated_date = validate_date(date)
            if validated_date is None:
                return False
            date = validated_date
        
        if not validate_description(description):
            return False
        
        expense_id = self.data_manager.add_expense(
            validated_amount,
            category,
            date,
            description
        )
        
        if expense_id is not None:
            print(f"成功添加支出记录，ID: {expense_id}")
            return True
        else:
            print("错误：添加支出记录失败")
            return False
    
    def list_expenses(
        self,
        date: Optional[str] = None,
        category: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "date",
        reverse: bool = True
    ) -> bool:
        """
        列出支出记录。
        
        Args:
            date: 日期过滤
            category: 类别过滤
            min_amount: 最小金额
            max_amount: 最大金额
            sort_by: 排序字段
            reverse: 是否降序
            
        Returns:
            成功返回 True
        """
        date_filter = None
        if date:
            date_filter = parse_date_filter(date)
            if date_filter is None:
                return False
        
        if category and category not in ALLOWED_CATEGORIES:
            print(f"错误：类别必须是以下之一：{', '.join(ALLOWED_CATEGORIES)}")
            return False
        
        expenses = self.data_manager.filter_expenses(
            date_filter=date_filter,
            category_filter=category,
            min_amount=min_amount,
            max_amount=max_amount
        )
        
        expenses = sort_expenses(expenses, sort_by, reverse)
        
        if not expenses:
            print("没有找到符合条件的支出记录")
            return True
        
        print(f"\n共找到 {len(expenses)} 条支出记录：")
        print("-" * 70)
        print(f"{'ID':<6} {'日期':<12} {'类别':<8} {'金额':<10} {'描述'}")
        print("-" * 70)
        
        total = 0.0
        for exp in expenses:
            exp_id = exp.get("id", 0)
            exp_date = exp.get("date", "")
            exp_category = exp.get("category", "")
            exp_amount = exp.get("amount", 0.0)
            exp_desc = exp.get("description", "")
            
            total += exp_amount
            print(f"{exp_id:<6} {exp_date:<12} {exp_category:<8} ¥{exp_amount:<9.2f} {exp_desc}")
        
        print("-" * 70)
        print(f"合计: ¥{total:.2f}")
        
        return True
    
    def summary(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> bool:
        """
        生成统计汇总。
        
        Args:
            year: 年份（可选）
            month: 月份（可选）
            
        Returns:
            成功返回 True
        """
        now = datetime.now()
        
        if year is None:
            year = now.year
        
        if month is not None:
            if month < 1 or month > 12:
                print("错误：月份必须在 1-12 之间")
                return False
            
            summary_data = calculate_monthly_summary(
                self.data_manager.get_all_expenses(),
                year,
                month
            )
            
            self._print_monthly_summary(summary_data)
        else:
            summary_data = calculate_yearly_summary(
                self.data_manager.get_all_expenses(),
                year
            )
            
            self._print_yearly_summary(summary_data)
        
        return True
    
    def _print_monthly_summary(self, summary: Dict[str, Any]) -> None:
        """
        打印月度汇总。
        
        Args:
            summary: 月度汇总数据
        """
        print(f"\n{'='*50}")
        print(f" {summary['year']}年{summary['month']}月支出汇总")
        print(f"{'='*50}")
        print(f" 总支出: ¥{summary['total_amount']:.2f}")
        print(f" 记录数: {summary['expense_count']} 笔")
        print(f" 最高支出日: {summary['highest_day'] or '无'} (¥{summary['highest_amount']:.2f})")
        print(f" 最低支出日: {summary['lowest_day'] or '无'} (¥{summary['lowest_amount']:.2f})")
        print(f"{'='*50}")
        
        if summary['category_totals']:
            print("\n 类别统计:")
            print(f"{'-'*40}")
            sorted_categories = sorted(
                summary['category_totals'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for category, amount in sorted_categories:
                percentage = summary['category_percentages'].get(category, (0, 0))[1]
                bar_length = int(percentage / 5)
                bar = "█" * bar_length
                print(f" {category:<6} ¥{amount:>8.2f} ({percentage:>5.1f}%) {bar}")
    
    def _print_yearly_summary(self, summary: Dict[str, Any]) -> None:
        """
        打印年度汇总。
        
        Args:
            summary: 年度汇总数据
        """
        print(f"\n{'='*50}")
        print(f" {summary['year']}年支出汇总")
        print(f"{'='*50}")
        print(f" 总支出: ¥{summary['total_amount']:.2f}")
        print(f" 记录数: {summary['expense_count']} 笔")
        
        if summary['highest_month']:
            print(f" 最高支出月: {summary['highest_month']}月 (¥{summary['highest_amount']:.2f})")
        if summary['lowest_month']:
            print(f" 最低支出月: {summary['lowest_month']}月 (¥{summary['lowest_amount']:.2f})")
        print(f"{'='*50}")
        
        if summary['category_totals']:
            print("\n 类别统计:")
            print(f"{'-'*40}")
            sorted_categories = sorted(
                summary['category_totals'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for category, amount in sorted_categories:
                percentage = summary['category_percentages'].get(category, (0, 0))[1]
                bar_length = int(percentage / 5)
                bar = "█" * bar_length
                print(f" {category:<6} ¥{amount:>8.2f} ({percentage:>5.1f}%) {bar}")
        
        print("\n 月度统计:")
        print(f"{'-'*40}")
        for month_num in range(1, 13):
            amount = summary['monthly_totals'].get(month_num, 0.0)
            bar_length = int(amount / 100) if amount > 0 else 0
            bar_length = min(bar_length, 20)
            bar = "█" * bar_length
            print(f" {month_num:>2}月: ¥{amount:>8.2f} {bar}")
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        删除支出记录。
        
        Args:
            expense_id: 支出记录 ID
            
        Returns:
            成功返回 True，失败返回 False
        """
        if not validate_id_exists(expense_id, self.data_manager.get_all_expenses()):
            return False
        
        expense = self.data_manager.get_expense_by_id(expense_id)
        if expense:
            print(f"\n即将删除以下记录：")
            print(f"  ID: {expense.get('id')}")
            print(f"  日期: {expense.get('date')}")
            print(f"  类别: {expense.get('category')}")
            print(f"  金额: ¥{expense.get('amount', 0):.2f}")
            print(f"  描述: {expense.get('description')}")
            
            confirm = input("\n确认删除？(y/N): ").strip().lower()
            if confirm != 'y':
                print("已取消删除")
                return False
        
        if self.data_manager.delete_expense(expense_id):
            print(f"成功删除 ID {expense_id} 的支出记录")
            return True
        else:
            print("删除失败")
            return False
    
    def export_report(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> bool:
        """
        导出报表到 Markdown 文件。
        
        Args:
            year: 年份（可选）
            month: 月份（可选）
            
        Returns:
            成功返回 True，失败返回 False
        """
        now = datetime.now()
        
        if year is None:
            year = now.year
        
        if month is not None:
            if month < 1 or month > 12:
                print("错误：月份必须在 1-12 之间")
                return False
            
            summary_data = calculate_monthly_summary(
                self.data_manager.get_all_expenses(),
                year,
                month
            )
            
            markdown_content = generate_monthly_markdown(summary_data)
            filename = f"expense_report_{year}_{month:02d}.md"
        else:
            summary_data = calculate_yearly_summary(
                self.data_manager.get_all_expenses(),
                year
            )
            
            markdown_content = generate_yearly_markdown(summary_data)
            filename = f"expense_report_{year}.md"
        
        if save_markdown_report(markdown_content, filename):
            print(f"报表已导出至: output_build/{filename}")
            return True
        else:
            print("导出报表失败")
            return False
