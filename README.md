# Python CLI Portfolio Tracker

A command-line tool to track your stock portfolio and view key financial metrics using the Finnhub API.

---

## ✨ Features

* Track stock transactions (buy, sell, delete).
* View a real-time portfolio summary with current market values.
* Calculate both unrealized and realized profit/loss.
* Fetch and display key financial metrics for any stock in a clean, categorized view.
* Data is saved locally in simple `portfolio.json` and `stats.json` files.

---

## 🚀 Getting Started

Follow these instructions to get the project set up and running on your local machine.

### Prerequisites

* Python 3.8+
* A free API key from **[Finnhub.io](https://finnhub.io)**

### Installation & Setup

1.  **Clone the repository** (or simply download the `api.py`, `portfolio.py`, and `main.py` files into a new directory).

2.  **Create a `requirements.txt` file** in your project directory with the following content:
    ```
    typer[all]>=0.9.0
    finnhub-python>=2.4.0
    ```

3.  **Install the required packages** by running the following command in your terminal:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your Finnhub API Key**
    This tool requires a Finnhub API key to fetch stock data. You must store this key in an environment variable named **`FINNHUB_API_KEY`**.

    **On macOS/Linux:**
    ```bash
    export FINNHUB_API_KEY="YOUR_API_KEY_HERE"
    ```
    *(To make this permanent, add the line above to your shell's startup file, such as `~/.zshrc` or `~/.bashrc`, then restart your terminal.)*

    **On Windows (Command Prompt):**
    ```cmd
    setx FINNHUB_API_KEY "YOUR_API_KEY_HERE"
    ```
    *(You will need to close and reopen your terminal for this change to take effect.)*

---

## 💻 Commands & Usage

All commands are run from your terminal.

### `view`

Displays a summary of all your holdings with current market values, unrealized P/L, and total realized P/L.

```bash
python main.py view
```

### add

Adds a new **buy** transaction to your portfolio.

```bash
python main.py add <TICKER> <SHARES> <PRICE>
```

`<TICKER>`: The stock symbol (e.g., AAPL)

`<SHARES>`: The number of shares purchased

`<PRICE>`: The price per share

Optional: Specify a past purchase date with the --date flag.

Example: --date 2023-10-25

Example:

```bash
python main.py add GOOGL 10 140.50 --date 2023-09-01
```

### sell

Records a sell transaction.
This calculates the realized profit or loss based on the average cost of your holdings and updates your statistics.

```bash
python main.py sell <TICKER> <SHARES> <PRICE>
```

Example:

```bash
python main.py sell GOOGL 5 155.00
```

### stats

Fetches and displays a categorized view of key financial metrics for any given ticker.

```bash
python main.py stats <TICKER>
```

Example:

```bash
python main.py stats MSFT
```


### delete

Removes all transactions for a specific ticker from your portfolio.
⚠️ This action is permanent and cannot be undone.

```bash
python main.py delete <TICKER>
```

### reset

Resets the all-time realized profit/loss counter in stats.json back to zero.
⚠️ This action is permanent.

```bash
python main.py reset
```

### Get Help

To see all available commands and their options directly from the CLI:

```bash
python main.py --help
```
