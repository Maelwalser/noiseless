import os
import sys
import finnhub
from finnhub.exceptions import FinnhubAPIException

# Create a single, reusable client instance
finnhub_client = None

def get_api_key() -> str:
    """Retrieves the Finnhub API key from environment variables."""
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        print("🚨 Error: FINNHUB_API_KEY environment variable not set.")
        sys.exit(1)
    return api_key

def setup_client():
    """Initializes the Finnhub client."""
    global finnhub_client
    if finnhub_client is None:
        finnhub_client = finnhub.Client(api_key=get_api_key())

def get_current_price(ticker: str) -> float | None:
    """Fetches the latest price for a given stock ticker using the REST API."""
    setup_client()
    try:
        quote = finnhub_client.quote(ticker)
        # The 'c' key stands for 'current price' in the Finnhub response
        if 'c' in quote and quote['c'] != 0:
            return float(quote['c'])
        else:
            print(f"❓ No price data for {ticker}. Response: {quote}")
            return None
    except FinnhubAPIException as e:
        print(f"🚨 Finnhub API error for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"🚨 An unexpected error occurred fetching price for {ticker}: {e}")
        return None

def get_basic_financials(ticker: str) -> dict | None:
    """Fetches basic financial metrics for a given stock ticker."""
    setup_client()
    try:
        financials = finnhub_client.company_basic_financials(ticker, 'all')
        # Check if the response contains the metric data
        if 'metric' in financials and financials['metric']:
            return financials['metric']
        else:
            print(f"❓ No financial metrics found for {ticker}. Response: {financials}")
            return None
    except FinnhubAPIException as e:
        print(f"🚨 Finnhub API error fetching financials for {ticker}: {e}")
        return None
    except Exception as e:
        print(f"🚨 An unexpected error occurred fetching financials for {ticker}: {e}")
        return None
