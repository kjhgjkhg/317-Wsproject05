"""
data_manager.py - JSON 数据持久化管理模块

负责 JSON 文件的读写、支出记录的增删改查和过滤操作。
"""

import json
import os
from typing import List, Dict, Any, Optional

from utils.config import SOURCE_DATA_DIR, EXPENSES_FILE, ALLOWED_CATEGORIES
from core_expense import Expense, create_expense


class DataManager:
    """
    数据管理类，负责支出数据的持久化和查询操作。
    """
    
    def __init__(self) -> None:
        """
        初始化数据管理器，自动加载数据。
        """
        self._expenses: List[Dict[str, Any]] = []
        self._next_id: int = 1
        self._ensure_data_directory()
        self._load_data()
    
    def _ensure_data_directory(self) -> None:
        """
        确保数据目录存在。
        """
        try:
            if not os.path.exists(SOURCE_DATA_DIR):
                os.makedirs(SOURCE_DATA_DIR)
        except OSError as e:
            print(f"错误：无法创建数据目录 - {e}")
    
    def _load_data(self) -> None:
        """
        从 JSON 文件加载数据。
        """
        if not os.path.exists(EXPENSES_FILE):
            self._expenses = []
            self._next_id = 1
            self._save_data()
            return
        
        try:
            with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                self._expenses = data.get("expenses", [])
                self._next_id = data.get("next_id", 1)
            elif isinstance(data, list):
                self._expenses = data
                self._next_id = self._calculate_next_id()
            else:
                self._expenses = []
                self._next_id = 1
                
        except json.JSONDecodeError:
            print("警告：数据文件格式错误，将使用空数据")
            self._expenses = []
            self._next_id = 1
        except Exception as e:
            print(f"警告：加载数据失败 - {e}")
            self._expenses = []
            self._next_id = 1
    
    def _calculate_next_id(self) -> int:
        """
        计算下一个可用的 ID。
        
        Returns:
            下一个 ID 值
        """
        if not self._expenses:
            return 1
        max_id = max(
            (exp.get("id", 0) for exp in self._expenses),
            default=0
        )
        return max_id + 1
    
    def _save_data(self) -> bool:
        """
        保存数据到 JSON 文件。
        
        Returns:
            成功返回 True，失败返回 False
        """
        try:
            data = {
                "expenses": self._expenses,
                "next_id": self._next_id
            }
            with open(EXPENSES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"错误：保存数据失败 - {e}")
            return False
    
    def add_expense(
        self,
        amount: float,
        category: str,
        date: str,
        description: str = ""
    ) -> Optional[int]:
        """
        添加新的支出记录。
        
        Args:
            amount: 金额
            category: 类别
            date: 日期
            description: 描述
            
        Returns:
            成功返回新记录的 ID，失败返回 None
        """
        expense = create_expense(
            self._next_id,
            amount,
            category,
            date,
            description
        )
        
        if expense is None:
            return None
        
        self._expenses.append(expense.to_dict())
        self._next_id += 1
        
        if self._save_data():
            return expense.id
        else:
            self._expenses.pop()
            self._next_id -= 1
            return None
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        根据 ID 删除支出记录。
        
        Args:
            expense_id: 支出记录 ID
            
        Returns:
            成功返回 True，失败返回 False
        """
        for i, expense in enumerate(self._expenses):
            if expense.get("id") == expense_id:
                deleted = self._expenses.pop(i)
                if self._save_data():
                    return True
                else:
                    self._expenses.insert(i, deleted)
                    return False
        
        print(f"错误：ID {expense_id} 不存在")
        return False
    
    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """
        获取所有支出记录。
        
        Returns:
            支出记录列表
        """
        return self._expenses.copy()
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取支出记录。
        
        Args:
            expense_id: 支出记录 ID
            
        Returns:
            支出记录字典，不存在返回 None
        """
        for expense in self._expenses:
            if expense.get("id") == expense_id:
                return expense.copy()
        return None
    
    def filter_expenses(
        self,
        date_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        根据条件过滤支出记录。
        
        Args:
            date_filter: 日期过滤（支持 YYYY-MM-DD 或 YYYY-MM）
            category_filter: 类别过滤
            min_amount: 最小金额
            max_amount: 最大金额
            
        Returns:
            过滤后的支出记录列表
        """
        result = []
        
        for expense in self._expenses:
            if date_filter:
                expense_date = expense.get("date", "")
                if len(date_filter) == 7:
                    if not expense_date.startswith(date_filter):
                        continue
                elif len(date_filter) == 10:
                    if expense_date != date_filter:
                        continue
            
            if category_filter:
                if expense.get("category") != category_filter:
                    continue
            
            amount = expense.get("amount", 0.0)
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue
            
            result.append(expense.copy())
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取基本统计信息。
        
        Returns:
            统计信息字典
        """
        total_amount = 0.0
        category_counts: Dict[str, int] = {}
        
        for expense in self._expenses:
            amount = expense.get("amount", 0.0)
            category = expense.get("category", "其他")
            
            total_amount += amount
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_count": len(self._expenses),
            "total_amount": round(total_amount, 2),
            "category_counts": category_counts
        }
    
    def get_next_id(self) -> int:
        """
        获取下一个可用的 ID。
        
        Returns:
            下一个 ID 值
        """
        return self._next_id
