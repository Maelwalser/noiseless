import json
from pathlib import Path
from datetime import datetime
import typer 
import os   

# Get the cross-platform application directory for this tool
APP_NAME = "money-cli"
APP_DIR = Path(typer.get_app_dir(APP_NAME))
APP_DIR.mkdir(parents=True, exist_ok=True) # Ensure the directory exists

# Update file paths to point to the new app directory
PORTFOLIO_FILE = APP_DIR / "portfolio.json"
STATS_FILE = APP_DIR / "stats.json"


def load_portfolio() -> list[dict]:
    """Loads the portfolio data from the JSON file."""
    if not PORTFOLIO_FILE.exists():
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def save_portfolio(data: list[dict]):
    """Saves the portfolio data to the JSON file."""
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_transaction(transaction: dict):
    """Adds a new transaction record to the portfolio."""
    data = load_portfolio()
    data.append(transaction)
    save_portfolio(data)

def delete_ticker(ticker_to_delete: str) -> bool:
    """Deletes all transactions for a given ticker."""
    transactions = load_portfolio()
    # Create a new list excluding the ticker to be deleted
    updated_transactions = [t for t in transactions if t['ticker'] != ticker_to_delete.upper()]
    
    if len(updated_transactions) < len(transactions):
        save_portfolio(updated_transactions)
        return True # Indicate that a deletion occurred
    return False # Ticker was not found

def load_stats() -> dict:
    """Loads realized profit/loss stats."""
    if not STATS_FILE.exists():
        return {"realized_pl": 0.0}
    with open(STATS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"realized_pl": 0.0}

def save_stats(data: dict):
    """Saves realized profit/loss stats."""
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def reset_stats():
    """Resets the realized P/L in the stats file to zero."""
    stats = load_stats()
    stats["realized_pl"] = 0.0
    save_stats(stats)

def sell_shares(ticker_to_sell: str, shares_to_sell: int, price_sold_at: float) -> float | None:
    """
    Sells a number of shares of a stock using average cost basis.
    Returns the realized profit/loss for this transaction, or None if error.
    """
    transactions = load_portfolio()
    ticker_to_sell = ticker_to_sell.upper()
    
    # Isolate transactions for the relevant ticker
    holdings_for_ticker = [t for t in transactions if t['ticker'] == ticker_to_sell]
    if not holdings_for_ticker:
        print(f"Error: You do not own any shares of {ticker_to_sell}.")
        return None

    # Calculate current holdings and average cost
    total_shares = sum(t['shares'] for t in holdings_for_ticker)
    total_cost = sum(t['shares'] * t['price'] for t in holdings_for_ticker)
    
    if shares_to_sell > total_shares:
        print(f"Error: You are trying to sell {shares_to_sell} shares of {ticker_to_sell}, but you only own {total_shares}.")
        return None
        
    avg_cost_basis = total_cost / total_shares
    
    # Calculate realized P/L for this sale
    realized_pl_for_sale = (price_sold_at - avg_cost_basis) * shares_to_sell
    
    # Update all-time stats
    stats = load_stats()
    stats["realized_pl"] += realized_pl_for_sale
    save_stats(stats)
    
    # Create the new state of the portfolio
    # 1. Remove all old transactions for this ticker
    other_transactions = [t for t in transactions if t['ticker'] != ticker_to_sell]
    
    # 2. If shares remain, add a new consolidated transaction
    remaining_shares = total_shares - shares_to_sell
    if remaining_shares > 0:
        consolidated_transaction = {
            "ticker": ticker_to_sell,
            "shares": remaining_shares,
            "price": avg_cost_basis, # The cost basis for remaining shares is the original average
            "date": datetime.now().isoformat()
        }
        other_transactions.append(consolidated_transaction)
    
    save_portfolio(other_transactions)
    
    return realized_pl_for_sale
