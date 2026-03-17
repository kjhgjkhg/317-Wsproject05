"""
Core Expense data class and business logic for Expense Tracker.

Defines the Expense dataclass with validation and serialization methods.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Optional

from utils.config import DATE_FORMAT
from utils.validators import validate_all_inputs


@dataclass
class Expense:
    """
    Represents a single expense record.

    Attributes:
        id: Unique auto-incrementing integer identifier.
        amount: The expense amount (must be > 0).
        category: The expense category from allowed list.
        date: Date of expense in YYYY-MM-DD format.
        description: Optional description (max 100 chars).
    """
    id: int
    amount: float
    category: str
    date: str
    description: str

    def __post_init__(self) -> None:
        """
        Post-initialization validation.
        Ensures all fields meet constraints.
        """
        if self.id < 1:
            raise ValueError("ID must be a positive integer")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if len(self.description) > 100:
            raise ValueError("Description must not exceed 100 characters")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Expense to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the expense.
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        """
        Create Expense from dictionary (e.g., from JSON).

        Args:
            data: Dictionary containing expense data.

        Returns:
            New Expense instance.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        required_fields = ["id", "amount", "category", "date", "description"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return cls(
            id=int(data["id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            date=str(data["date"]),
            description=str(data["description"]),
        )

    @classmethod
    def create_new(
        cls,
        next_id: int,
        amount_str: str,
        category: str,
        date_str: str,
        description: str,
    ) -> tuple:
        """
        Factory method to create a new Expense with validation.

        Args:
            next_id: The next available ID for the new expense.
            amount_str: Amount as string (will be validated and parsed).
            category: Category string (will be validated).
            date_str: Date string (will be validated).
            description: Description string (will be validated).

        Returns:
            Tuple of (success: bool, result: Expense or error_message: str).
        """
        is_valid, parsed_values, error_message = validate_all_inputs(
            amount_str=amount_str,
            category=category,
            date_str=date_str,
            description=description,
        )

        if not is_valid:
            return False, error_message

        try:
            expense = cls(
                id=next_id,
                amount=parsed_values["amount"],
                category=category,
                date=date_str,
                description=description,
            )
            return True, expense
        except ValueError as e:
            return False, str(e)

    def __str__(self) -> str:
        """
        String representation of the expense.

        Returns:
            Human-readable string format.
        """
        return (
            f"[ID:{self.id}] {self.date} | {self.category} | "
            f"¥{self.amount:.2f} | {self.description}"
        )

    def __repr__(self) -> str:
        """
        Detailed representation for debugging.

        Returns:
            Detailed string representation.
        """
        return (
            f"Expense(id={self.id}, amount={self.amount}, "
            f"category='{self.category}', date='{self.date}', "
            f"description='{self.description}')"
        )
