import typer
from rich.console import Console
from rich.table import Table
from rich import box
from typing import Optional
from datetime import date

from .models import Transaction, CATEGORIES, TransactionType
from . import storage

app = typer.Typer(
    name="expense-tracker",
    help="Track your income and expenses from the terminal.",
    add_completion=False,
)
console = Console()


def _category_prompt() -> str:
    console.print("\n[bold]Categories:[/bold]")
    for i, cat in enumerate(CATEGORIES, 1):
        console.print(f"  [cyan]{i}[/cyan]. {cat}")
    choice = typer.prompt("Pick a category number", type=int)
    if 1 <= choice <= len(CATEGORIES):
        return CATEGORIES[choice - 1]
    console.print("[red]Invalid choice, using 'Other'[/red]")
    return "Other"


@app.command()
def add(
    amount: float = typer.Argument(..., help="Amount (positive number)"),
    description: str = typer.Argument(..., help="Short description"),
    income: bool = typer.Option(False, "--income", "-i", help="Mark as income instead of expense"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category name"),
    transaction_date: Optional[str] = typer.Option(None, "--date", "-d", help="Date YYYY-MM-DD (default: today)"),
):
    """Add a new expense or income entry."""
    if amount <= 0:
        console.print("[red]Amount must be positive.[/red]")
        raise typer.Exit(1)

    if category is None:
        category = _category_prompt()
    elif category not in CATEGORIES:
        console.print(f"[yellow]Unknown category '{category}', using 'Other'.[/yellow]")
        category = "Other"

    entry_date = transaction_date or date.today().isoformat()
    tx_type: TransactionType = "income" if income else "expense"

    t = Transaction(
        amount=amount,
        category=category,
        description=description,
        type=tx_type,
        date=entry_date,
    )
    storage.add_transaction(t)

    icon = "[green]+[/green]" if tx_type == "income" else "[red]-[/red]"
    console.print(f"\n{icon} [{tx_type}] [bold]{description}[/bold] — ${amount:.2f} [{category}] on {entry_date}  [dim](id: {t.id})[/dim]")


@app.command(name="list")
def list_transactions(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Filter by month YYYY-MM"),
    income_only: bool = typer.Option(False, "--income", help="Show only income"),
    expense_only: bool = typer.Option(False, "--expense", help="Show only expenses"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max rows to show"),
):
    """List transactions."""
    transactions = storage.load_all()

    if category:
        transactions = [t for t in transactions if t.category.lower() == category.lower()]
    if month:
        transactions = [t for t in transactions if t.date.startswith(month)]
    if income_only:
        transactions = [t for t in transactions if t.type == "income"]
    if expense_only:
        transactions = [t for t in transactions if t.type == "expense"]

    transactions = sorted(transactions, key=lambda t: t.date, reverse=True)[:limit]

    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Date", width=12)
    table.add_column("Type", width=9)
    table.add_column("Category", width=14)
    table.add_column("Description")
    table.add_column("Amount", justify="right", width=12)

    for t in transactions:
        color = "green" if t.type == "income" else "red"
        sign = "+" if t.type == "income" else "-"
        table.add_row(
            t.id,
            t.date,
            f"[{color}]{t.type}[/{color}]",
            t.category,
            t.description,
            f"[{color}]{sign}${t.amount:.2f}[/{color}]",
        )

    console.print(table)
    console.print(f"[dim]{len(transactions)} transaction(s) shown.[/dim]")


@app.command()
def summary(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Filter by month YYYY-MM"),
):
    """Show a summary of income, expenses, and balance by category."""
    transactions = storage.load_all()

    if month:
        transactions = [t for t in transactions if t.date.startswith(month)]

    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return

    by_category: dict[str, dict] = {}
    total_income = 0.0
    total_expense = 0.0

    for t in transactions:
        if t.category not in by_category:
            by_category[t.category] = {"income": 0.0, "expense": 0.0}
        by_category[t.category][t.type] += t.amount
        if t.type == "income":
            total_income += t.amount
        else:
            total_expense += t.amount

    title = f"Summary — {month}" if month else "Summary — All time"
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Category", width=16)
    table.add_column("Income", justify="right", width=12)
    table.add_column("Expenses", justify="right", width=12)
    table.add_column("Net", justify="right", width=12)

    for cat, amounts in sorted(by_category.items()):
        net = amounts["income"] - amounts["expense"]
        net_str = f"[green]+${net:.2f}[/green]" if net >= 0 else f"[red]-${abs(net):.2f}[/red]"
        table.add_row(
            cat,
            f"[green]+${amounts['income']:.2f}[/green]" if amounts["income"] else "—",
            f"[red]-${amounts['expense']:.2f}[/red]" if amounts["expense"] else "—",
            net_str,
        )

    console.print(table)

    balance = total_income - total_expense
    balance_str = f"[bold green]+${balance:.2f}[/bold green]" if balance >= 0 else f"[bold red]-${abs(balance):.2f}[/bold red]"
    console.print(f"\n  Total income:   [green]+${total_income:.2f}[/green]")
    console.print(f"  Total expenses: [red]-${total_expense:.2f}[/red]")
    console.print(f"  Balance:        {balance_str}\n")


@app.command()
def delete(
    transaction_id: str = typer.Argument(..., help="Transaction ID to delete"),
):
    """Delete a transaction by its ID."""
    if storage.delete_transaction(transaction_id):
        console.print(f"[green]Deleted transaction [bold]{transaction_id}[/bold].[/green]")
    else:
        console.print(f"[red]No transaction found with ID '{transaction_id}'.[/red]")
        raise typer.Exit(1)


@app.command()
def balance(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Filter by month YYYY-MM"),
):
    """Show current balance (income minus expenses)."""
    transactions = storage.load_all()
    if month:
        transactions = [t for t in transactions if t.date.startswith(month)]

    income = sum(t.amount for t in transactions if t.type == "income")
    expenses = sum(t.amount for t in transactions if t.type == "expense")
    bal = income - expenses

    period = month or "all time"
    console.print(f"\n  [bold]Balance ({period})[/bold]")
    console.print(f"  Income:   [green]+${income:.2f}[/green]")
    console.print(f"  Expenses: [red]-${expenses:.2f}[/red]")
    if bal >= 0:
        console.print(f"  Balance:  [bold green]+${bal:.2f}[/bold green]\n")
    else:
        console.print(f"  Balance:  [bold red]-${abs(bal):.2f}[/bold red]\n")
