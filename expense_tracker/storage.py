import json
import os
from pathlib import Path
from typing import List, Optional

from .models import Transaction

DATA_DIR = Path.home() / ".expense_tracker"
DATA_FILE = DATA_DIR / "data.json"


def _ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]")


def load_all() -> List[Transaction]:
    _ensure_data_file()
    raw = json.loads(DATA_FILE.read_text())
    return [Transaction.from_dict(item) for item in raw]


def save_all(transactions: List[Transaction]):
    _ensure_data_file()
    DATA_FILE.write_text(
        json.dumps([t.to_dict() for t in transactions], indent=2)
    )


def add_transaction(transaction: Transaction):
    transactions = load_all()
    transactions.append(transaction)
    save_all(transactions)


def delete_transaction(transaction_id: str) -> bool:
    transactions = load_all()
    filtered = [t for t in transactions if t.id != transaction_id]
    if len(filtered) == len(transactions):
        return False
    save_all(filtered)
    return True


def find_by_id(transaction_id: str) -> Optional[Transaction]:
    return next((t for t in load_all() if t.id == transaction_id), None)
