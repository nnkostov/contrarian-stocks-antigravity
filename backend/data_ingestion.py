import pandas as pd
import yfinance as yf
import requests

def get_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia.
    """
    # Fallback/Alternative source: GitHub Datasets
    url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
    try:
        df = pd.read_csv(url)
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500 list: {e}")
        return []

def fetch_stock_data(ticker):
    """
    Fetches historical data and info for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch 1 year of history for 52-week metrics and RSI calculation
        hist = stock.history(period="1y")
        info = stock.info
        return hist, info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None, None

def fetch_bulk_history(tickers, period="1y"):
    """
    Fetches historical data for multiple tickers at once.
    """
    try:
        # download returns a MultiIndex DataFrame
        # threads=False to avoid SQLite database locking errors in yfinance cache
        data = yf.download(tickers, period=period, group_by='ticker', progress=False, threads=False)
        return data
    except Exception as e:
        print(f"Error fetching bulk data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Quick test
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers.")
    if tickers:
        print(f"Fetching data for {tickers[0]}...")
        data, info = fetch_stock_data(tickers[0])
        print("Done.")
