"""
Data Manager module for Expense Tracker.

Handles all JSON file operations, CRUD operations, and data persistence.
This is the only module that directly interacts with the data file.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple

from utils.config import EXPENSES_FILE_PATH, DATA_DIR, ERROR_MESSAGES
from core_expense import Expense


class DataManager:
    """
    Manages expense data persistence and CRUD operations.

    This class handles all interactions with the JSON data file,
    ensuring data integrity and proper error handling.
    """

    def __init__(self) -> None:
        """
        Initialize the DataManager.
        Creates data directory if it doesn't exist.
        """
        self._expenses: List[Dict[str, Any]] = []
        self._next_id: int = 1
        self._ensure_data_directory()
        self._load_data()

    def _ensure_data_directory(self) -> None:
        """
        Ensure the data directory exists.
        Creates it if necessary.
        """
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except OSError as e:
            print(f"错误: 无法创建数据目录 - {e}")
            raise

    def _load_data(self) -> None:
        """
        Load expense data from JSON file.
        If file doesn't exist or is corrupted, start with empty data.
        """
        if not os.path.exists(EXPENSES_FILE_PATH):
            self._expenses = []
            self._next_id = 1
            return

        try:
            with open(EXPENSES_FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self._expenses = []
                    self._next_id = 1
                    return

                data = json.loads(content)

                if not isinstance(data, list):
                    print("警告: 数据文件格式错误，使用空数据")
                    self._expenses = []
                    self._next_id = 1
                    return

                self._expenses = data
                self._calculate_next_id()

        except json.JSONDecodeError as e:
            print(f"警告: JSON解析错误 - {e}，使用空数据")
            self._expenses = []
            self._next_id = 1
        except PermissionError:
            print(f"错误: {ERROR_MESSAGES['permission_denied']}")
            self._expenses = []
            self._next_id = 1
        except Exception as e:
            print(f"错误: 读取数据文件失败 - {e}")
            self._expenses = []
            self._next_id = 1

    def _calculate_next_id(self) -> None:
        """
        Calculate the next available ID based on existing expenses.
        """
        if not self._expenses:
            self._next_id = 1
            return

        max_id = 0
        for expense in self._expenses:
            if isinstance(expense, dict) and "id" in expense:
                try:
                    expense_id = int(expense["id"])
                    if expense_id > max_id:
                        max_id = expense_id
                except (ValueError, TypeError):
                    continue

        self._next_id = max_id + 1

    def _save_data(self) -> Tuple[bool, str]:
        """
        Save current expenses to JSON file.

        Returns:
            Tuple of (success, error_message).
        """
        try:
            with open(EXPENSES_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._expenses, f, ensure_ascii=False, indent=2)
            return True, ""
        except PermissionError:
            return False, ERROR_MESSAGES["permission_denied"]
        except Exception as e:
            return False, f"{ERROR_MESSAGES['file_access_error']}: {e}"

    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """
        Get all expense records.

        Returns:
            List of all expense dictionaries.
        """
        return self._expenses.copy()

    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single expense by ID.

        Args:
            expense_id: The ID to search for.

        Returns:
            Expense dictionary if found, None otherwise.
        """
        for expense in self._expenses:
            if expense.get("id") == expense_id:
                return expense.copy()
        return None

    def get_all_ids(self) -> List[int]:
        """
        Get list of all expense IDs.

        Returns:
            List of integer IDs.
        """
        ids = []
        for expense in self._expenses:
            try:
                ids.append(int(expense.get("id", 0)))
            except (ValueError, TypeError):
                continue
        return ids

    def add_expense(self, expense: Expense) -> Tuple[bool, str]:
        """
        Add a new expense to the database.

        Args:
            expense: The Expense object to add.

        Returns:
            Tuple of (success, error_message).
        """
        try:
            expense_dict = expense.to_dict()
            self._expenses.append(expense_dict)

            success, error = self._save_data()
            if success:
                self._next_id += 1
                return True, ""
            else:
                # Rollback on save failure
                self._expenses.pop()
                return False, error
        except Exception as e:
            return False, f"添加支出失败: {e}"

    def delete_expense(self, expense_id: int) -> Tuple[bool, str]:
        """
        Delete an expense by ID.

        Args:
            expense_id: The ID of the expense to delete.

        Returns:
            Tuple of (success, error_message).
        """
        original_expenses = self._expenses.copy()

        found = False
        for i, expense in enumerate(self._expenses):
            if expense.get("id") == expense_id:
                self._expenses.pop(i)
                found = True
                break

        if not found:
            return False, ERROR_MESSAGES["expense_not_found"]

        success, error = self._save_data()
        if success:
            return True, ""
        else:
            # Rollback on save failure
            self._expenses = original_expenses
            return False, error

    def get_next_id(self) -> int:
        """
        Get the next available ID for a new expense.

        Returns:
            The next integer ID.
        """
        return self._next_id

    def reload_data(self) -> None:
        """
        Reload data from file.
        Useful for external changes or recovery.
        """
        self._load_data()
