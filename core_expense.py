"""Expense data class definition."""
from typing import Dict, Any


class Expense:
    """Expense record data class."""

    def __init__(self, id: int, amount: float, category: str, date: str, description: str = ""):
        self.id = id
        self.amount = float(amount)
        self.category = category
        self.date = date
        self.description = description or ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Deserialize from dictionary."""
        return cls(
            id=data.get("id", 0),
            amount=data.get("amount", 0.0),
            category=data.get("category", ""),
            date=data.get("date", ""),
            description=data.get("description", "")
        )

    def __str__(self) -> str:
        """String representation."""
        return f"ID: {self.id}, 日期: {self.date}, 类别: {self.category}, 金额: ¥{self.amount:.2f}, 描述: {self.description}"
