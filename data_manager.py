"""Data manager for JSON persistence."""
import json
import os
from typing import List, Optional

from core_expense import Expense
from utils.util_config import DATA_FILE, ensure_directories


class DataManager:
    """Manage expense data persistence."""

    def __init__(self, file_path: str = DATA_FILE):
        self.file_path = file_path
        ensure_directories()
        self._expenses: List[Expense] = []
        self.load_data()

    def load_data(self) -> List[Expense]:
        """Load expenses from JSON file."""
        self._expenses = []
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            try:
                                exp = Expense.from_dict(item)
                                self._expenses.append(exp)
                            except Exception:
                                pass
        except Exception:
            pass
        return self._expenses

    def save_data(self, expenses: Optional[List[Expense]] = None) -> None:
        """Save expenses to JSON file."""
        try:
            if expenses is not None:
                self._expenses = expenses
            data = [exp.to_dict() for exp in self._expenses]
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_next_id(self) -> int:
        """Get next auto-incrementing ID."""
        max_id = 0
        for exp in self._expenses:
            if exp.id > max_id:
                max_id = exp.id
        return max_id + 1

    def add_expense(self, expense: Expense) -> None:
        """Add an expense and save."""
        try:
            self._expenses.append(expense)
            self.save_data()
        except Exception:
            pass

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by ID."""
        try:
            original_len = len(self._expenses)
            self._expenses = [e for e in self._expenses if e.id != expense_id]
            if len(self._expenses) < original_len:
                self.save_data()
                return True
        except Exception:
            pass
        return False

    def get_all_expenses(self) -> List[Expense]:
        """Get all expenses."""
        return self._expenses[:]
