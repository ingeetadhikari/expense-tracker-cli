from dataclasses import dataclass, field
from datetime import date
from typing import Literal
import uuid


TransactionType = Literal["expense", "income"]

CATEGORIES = [
    "Food", "Transport", "Housing", "Health",
    "Entertainment", "Shopping", "Education", "Salary",
    "Freelance", "Other"
]


@dataclass
class Transaction:
    amount: float
    category: str
    description: str
    type: TransactionType
    date: str = field(default_factory=lambda: date.today().isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "type": self.type,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            id=data["id"],
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            type=data["type"],
            date=data["date"],
        )
