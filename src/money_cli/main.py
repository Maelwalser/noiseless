import typer
import re
from typing_extensions import Annotated
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel # Import Panel

import portfolio
import api

# Create the Typer app
app = typer.Typer(
    name="Portfolio Tracker",
    help="A CLI tool for tracking stock portfolios."
)
console = Console()


def _format_metric_name(name: str) -> str:
    """Formats a camelCase metric name into a readable title."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    # Handle specific cases like 'Pcf' or 'Pe'
    s3 = s2.replace("Pcf", "PCF").replace("Pe ", "PE ").replace("Ps ", "PS ").replace("Roi", "ROI")
    return s3.title()


@app.command()
def add(
    ticker: Annotated[str, typer.Argument(help="The stock ticker symbol (e.g., 'AAPL').")],
    shares: Annotated[int, typer.Argument(help="The number of shares purchased.")],
    price: Annotated[float, typer.Argument(help="The price per share at the time of purchase.")],
    date: Annotated[datetime, typer.Option(help="The date of the transaction (YYYY-MM-DD).")] = datetime.now(),
):
    """
    Add a new stock transaction to your portfolio.
    """
    new_transaction = {
        "ticker": ticker.upper(), "shares": shares, "price": price, "date": date.isoformat(),
    }
    portfolio.add_transaction(new_transaction)
    console.print(f"✅ Added transaction: {shares} shares of {ticker.upper()} at ${price:.2f}")


@app.command()
def delete(
    ticker: Annotated[str, typer.Argument(help="The stock ticker symbol to remove completely (e.g., 'AAPL').")]
):
    """
    Delete all transactions for a specific ticker from the portfolio.
    """
    confirm = typer.confirm(f"Are you sure you want to delete all holdings for {ticker.upper()}? This action cannot be undone.")
    if not confirm:
        console.print("Cancelled.")
        raise typer.Abort()

    if portfolio.delete_ticker(ticker):
        console.print(f"🗑️ Successfully deleted all holdings for {ticker.upper()}.")
    else:
        console.print(f"⚠️ Could not find ticker {ticker.upper()} in portfolio.")


@app.command()
def sell(
    ticker: Annotated[str, typer.Argument(help="The stock ticker symbol to sell (e.g., 'AAPL').")],
    shares: Annotated[int, typer.Argument(help="The number of shares to sell.")],
    price: Annotated[float, typer.Argument(help="The price per share you sold at.")]
):
    """
    Sell a specified number of shares for a ticker.
    """
    realized_pl = portfolio.sell_shares(ticker, shares, price)

    if realized_pl is not None:
        if realized_pl >= 0:
            console.print(f"📈 Sold {shares} of {ticker.upper()} for a profit of [bold green]${realized_pl:,.2f}[/bold green].")
        else:
            console.print(f"📉 Sold {shares} of {ticker.upper()} for a loss of [bold red]${-realized_pl:,.2f}[/bold red].")


@app.command()
def view():
    """
    View all holdings in the portfolio with current market values.
    """
    transactions = portfolio.load_portfolio()
    stats = portfolio.load_stats()
    realized_pl = stats.get("realized_pl", 0.0)

    if not transactions:
        console.print("Portfolio is empty. Add a transaction with the 'add' command.", style="yellow")
        raise typer.Exit()

    holdings = defaultdict(lambda: {"shares": 0, "total_cost": 0.0})
    for t in transactions:
        holdings[t["ticker"]]["shares"] += t["shares"]
        holdings[t["ticker"]]["total_cost"] += t["shares"] * t["price"]

    unique_tickers = sorted(holdings.keys())

    title = f"Portfolio Summary (as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) | Realized P/L: ${realized_pl:,.2f}"
    table = Table(title=title)
    table.add_column("Ticker", style="cyan"); table.add_column("Shares", justify="right", style="magenta"); table.add_column("Avg. Cost", justify="right"); table.add_column("Total Cost", justify="right"); table.add_column("Current Price", justify="right", style="yellow"); table.add_column("Market Value", justify="right", style="green"); table.add_column("Gain/Loss", justify="right")

    total_market_value, total_cost_basis = 0.0, 0.0

    with console.status("[bold green]Fetching latest prices...[/]") as status:
        for ticker in unique_tickers:
            info = holdings[ticker]
            current_price = api.get_current_price(ticker)
            shares, total_cost = info["shares"], info["total_cost"]
            avg_cost = total_cost / shares
            total_cost_basis += total_cost
            market_value_str, gain_loss_str, gain_loss_style = "N/A", "N/A", "white"
            price_str = "[red]Error[/red]"

            if current_price is not None:
                market_value = shares * current_price
                total_market_value += market_value
                gain_loss = market_value - total_cost
                price_str = f"${current_price:,.2f}"
                market_value_str = f"${market_value:,.2f}"
                gain_loss_str = f"${gain_loss:,.2f}"
                gain_loss_style = "green" if gain_loss >= 0 else "red"

            table.add_row(ticker, str(shares), f"${avg_cost:,.2f}", f"${total_cost:,.2f}", price_str, market_value_str, gain_loss_str, style=gain_loss_style)

    total_unrealized_pl = total_market_value - total_cost_basis
    total_unrealized_pl_style = "green" if total_unrealized_pl >= 0 else "red"

    table.add_section()
    table.add_row(
        "[bold]TOTALS[/bold]", "", "", f"[bold]${total_cost_basis:,.2f}[/bold]", "", f"[bold green]${total_market_value:,.2f}[/bold green]", f"[bold {total_unrealized_pl_style}]${total_unrealized_pl:,.2f}[/bold {total_unrealized_pl_style}]"
    )

    console.print(table)


@app.command()
def stats(
    ticker: Annotated[str, typer.Argument(help="The stock ticker to get financial metrics for (e.g., 'AAPL').")]
):
    """
    Display a curated list of financial metrics for a specific ticker.
    """
    METRIC_CATEGORIES = {
        "💰 Valuation": [
            "52WeekHigh", "52WeekLow", "peTTM", "pegTTM", "psTTM", "psAnnual", "pcfRatioTTM",
        ],
        "💵 Dividends": [
            "currentDividendYieldTTM", "dividendPerShareTTM", "dividendPerShareAnnual", "dividendGrowthRate5Y",
        ],
        "📈 Profitability & Margins": [
            "operatingMarginTTM", "operatingMarginAnnual", "roiTTM", "roiAnnual",
        ],
        "🚀 Growth": [
            "revenueGrowthTtmYoy", "revenueGrowthQuarterlyYoy", "revenueGrowth3Y", "revenueGrowth5Y",
        ],
        "📊 Financial Health": [
            "cashFlowPerShareAnnual", "cashFlowPerShareQuarterly", "totalDebt/totalEquityAnnual", "totalDebt/totalEquityQuarterly",
        ]
    }

    with console.status(f"[bold green]Fetching financial metrics for {ticker.upper()}...[/]"):
        metrics = api.get_basic_financials(ticker)

    if not metrics:
        console.print(f"🚨 Could not retrieve financial data for {ticker.upper()}.", style="red")
        raise typer.Exit()

    console.print(f"\n[bold underline]Key Financials for {ticker.upper()}[/bold underline]\n")

    for category, keys in METRIC_CATEGORIES.items():
        # Create a simple table for the key-value pairs without a header or borders
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="magenta")

        rows_added = 0
        for key in keys:
            if key in metrics and metrics[key] is not None:
                value = metrics[key]
                formatted_key = _format_metric_name(key)

                if isinstance(value, float):
                    if any(k in key.lower() for k in ['yield', 'margin', 'growth', 'roi']):
                        formatted_value = f"{value:,.2f}%"
                    else:
                        formatted_value = f"{value:,.2f}"
                else:
                    formatted_value = str(value)

                table.add_row(formatted_key, formatted_value)
                rows_added += 1

        # Only display the panel if it contains data
        if rows_added > 0:
            console.print(
                Panel(
                    table,
                    title=f"[bold default]{category}[/bold default]",
                    border_style="blue",
                    expand=False
                )
            )


@app.command()
def reset():
    """
    Reset the all-time realized profit/loss to zero.
    """
    confirm = typer.confirm("Are you sure you want to reset your realized P/L to $0.00? This action cannot be undone.")
    if not confirm:
        console.print("Cancelled.")
        raise typer.Abort()

    portfolio.reset_stats()
    console.print("✅ Realized P/L has been reset to $0.00.")


if __name__ == "__main__":
    app()
