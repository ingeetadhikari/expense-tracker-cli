# expense-tracker-cli

A Python command-line tool to track your income and expenses with category summaries and balance reports.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Add an expense
```bash
python main.py add 50.00 "Lunch at restaurant"
```

### Add income
```bash
python main.py add 2000.00 "Monthly salary" --income --category Salary
```

### List transactions
```bash
python main.py list
python main.py list --month 2026-03
python main.py list --category Food
```

### Summary by category
```bash
python main.py summary
python main.py summary --month 2026-03
```

### Check balance
```bash
python main.py balance
python main.py balance --month 2026-03
```

### Delete a transaction
```bash
python main.py delete <transaction-id>
```

## Data Storage

Transactions are stored in `~/.expense_tracker/data.json`.

## Categories

Food, Transport, Housing, Health, Entertainment, Shopping, Education, Salary, Freelance, Other
