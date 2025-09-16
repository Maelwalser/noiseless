# Python CLI Portfolio Tracker
============================

A command-line tool to track your stock portfolio and view key financial metrics using the Finnhub API.

🚀 Quick Install & Use
----------------------

These instructions are for quickly installing and using the portfolio tracker as a command-line tool.

### Prerequisites

-   Python 3.8+

-   A free API key from [**Finnhub.io**](https://finnhub.io "null")

### Installation

You can install the package directly from this repository using pip:

```
pip install git+[https://github.com/maelwalser/noiseless.git](https://github.com/maelwalser/noiseless.git)

```

### Setup

1.  **Set up your Finnhub API Key** This tool requires a Finnhub API key to fetch stock data. You must store this key in an environment variable named **`FINNHUB_API_KEY`**.

    **On macOS/Linux:**

    ```
    export FINNHUB_API_KEY="YOUR_API_KEY_HERE"

    ```

    *(To make this permanent, add the line above to your shell's startup file, such as `~/.zshrc` or `~/.bashrc`, then restart your terminal.)*

    **On Windows (Command Prompt):**

    ```
    setx FINNHUB_API_KEY "YOUR_API_KEY_HERE"

    ```

    *(You will need to close and reopen your terminal for this change to take effect.)*

### Commands & Usage

Once installed, you can use the `money` command from your terminal.

| Command | Description | Example |
| :--- | :--- | :--- |
| `money view` | Displays a summary of all your holdings. | `money view` |
| `money add` | Adds a new `buy` transaction to your portfolio. | `money add AAPL 10 175.50 --date 2023-10-26` |
| `money sell` | Records a `sell` transaction. | `money sell AAPL 5 180.00` |
| `money stats` | Fetches key financial metrics for a ticker. | `money stats MSFT` |
| `money delete` | Removes all transactions for a specific ticker. | `money delete GOOGL` |
| `money reset` | Resets the all-time realized profit/loss counter to zero. | `money reset` |
| `money --help` | To see all available commands and their options directly from the CLI. | `money --help` |


🔧 Development Setup
--------------------

Follow these instructions to set up the project for development, allowing you to customize or contribute to it.

### Prerequisites

-   Python 3.8+

-   A free API key from [**Finnhub.io**](https://finnhub.io "null")

### Installation & Setup

1.  **Clone the repository**

    ```
    git clone [https://github.com/maelwalser/noiseless.git](https://github.com/maelwalser/noiseless.git)
    cd noiseless/noiseless-package

    ```

2.  **Create a `requirements.txt` file** in the `noiseless-package` directory with the following content:

    ```
    typer[all]>=0.9.0
    finnhub-python>=2.4.0

    ```

3.  **Install the required packages** (it is recommended to do this in a virtual environment):

    ```
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt

    ```

4.  **Set up your Finnhub API Key** as described in the "Quick Install & Use" section.

### Running from Source

All commands are run from the `src` directory.

```
cd src
python money_cli/main.py <command>

```

**Example:**

```
python money_cli/main.py view

```
