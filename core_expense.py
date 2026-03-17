"""
core_expense.py - Expense 数据类与业务校验模块

定义支出数据结构、序列化/反序列化及业务验证逻辑。
"""

from typing import Dict, Any, Optional
from datetime import datetime

from utils.config import DATE_FORMAT, ALLOWED_CATEGORIES, MAX_DESCRIPTION_LENGTH, MIN_AMOUNT


class Expense:
    """
    支出数据类，封装单条支出记录的所有属性和操作。
    """
    
    def __init__(
        self,
        expense_id: int,
        amount: float,
        category: str,
        date: str,
        description: str = ""
    ) -> None:
        """
        初始化支出记录。
        
        Args:
            expense_id: 唯一标识ID
            amount: 金额
            category: 类别
            date: 日期 (YYYY-MM-DD)
            description: 描述
        """
        self._id: int = expense_id
        self._amount: float = amount
        self._category: str = category
        self._date: str = date
        self._description: str = description
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, value: float) -> None:
        if value <= MIN_AMOUNT:
            raise ValueError(f"金额必须大于 {MIN_AMOUNT}")
        self._amount = round(value, 2)
    
    @property
    def category(self) -> str:
        return self._category
    
    @category.setter
    def category(self, value: str) -> None:
        if value not in ALLOWED_CATEGORIES:
            raise ValueError(f"类别必须是以下之一：{', '.join(ALLOWED_CATEGORIES)}")
        self._category = value
    
    @property
    def date(self) -> str:
        return self._date
    
    @date.setter
    def date(self, value: str) -> None:
        try:
            datetime.strptime(value, DATE_FORMAT)
            self._date = value
        except ValueError:
            raise ValueError("日期格式必须为 YYYY-MM-DD 且为有效日期")
    
    @property
    def description(self) -> str:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        if len(value) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"描述不能超过 {MAX_DESCRIPTION_LENGTH} 个字符")
        self._description = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将支出对象转换为字典。
        
        Returns:
            包含所有属性的字典
        """
        return {
            "id": self._id,
            "amount": self._amount,
            "category": self._category,
            "date": self._date,
            "description": self._description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """
        从字典创建支出对象。
        
        Args:
            data: 包含支出数据的字典
            
        Returns:
            Expense 实例
        """
        return cls(
            expense_id=data.get("id", 0),
            amount=data.get("amount", 0.0),
            category=data.get("category", "其他"),
            date=data.get("date", ""),
            description=data.get("description", "")
        )
    
    def validate(self) -> bool:
        """
        验证支出记录的所有字段是否有效。
        
        Returns:
            验证通过返回 True，否则返回 False
        """
        try:
            if self._amount <= MIN_AMOUNT:
                return False
            if self._category not in ALLOWED_CATEGORIES:
                return False
            datetime.strptime(self._date, DATE_FORMAT)
            if len(self._description) > MAX_DESCRIPTION_LENGTH:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"Expense(id={self._id}, amount={self._amount}, "
            f"category='{self._category}', date='{self._date}', "
            f"description='{self._description}')"
        )
    
    def __str__(self) -> str:
        return (
            f"[{self._id}] {self._date} | {self._category} | "
            f"¥{self._amount:.2f} | {self._description}"
        )


def validate_expense_data(
    amount: float,
    category: str,
    date: str,
    description: str
) -> Optional[str]:
    """
    验证支出数据并返回错误信息（如果有）。
    
    Args:
        amount: 金额
        category: 类别
        date: 日期
        description: 描述
        
    Returns:
        错误信息字符串，验证通过返回 None
    """
    if amount <= MIN_AMOUNT:
        return f"金额必须大于 {MIN_AMOUNT}"
    
    if category not in ALLOWED_CATEGORIES:
        return f"类别必须是以下之一：{', '.join(ALLOWED_CATEGORIES)}"
    
    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        return "日期格式必须为 YYYY-MM-DD 且为有效日期"
    
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return f"描述不能超过 {MAX_DESCRIPTION_LENGTH} 个字符"
    
    return None


def create_expense(
    expense_id: int,
    amount: float,
    category: str,
    date: str,
    description: str = ""
) -> Optional[Expense]:
    """
    创建并验证支出对象。
    
    Args:
        expense_id: 唯一标识ID
        amount: 金额
        category: 类别
        date: 日期
        description: 描述
        
    Returns:
        验证通过返回 Expense 对象，否则返回 None
    """
    error = validate_expense_data(amount, category, date, description)
    if error:
        print(f"错误：{error}")
        return None
    
    try:
        return Expense(expense_id, amount, category, date, description)
    except ValueError as e:
        print(f"错误：{e}")
        return None
