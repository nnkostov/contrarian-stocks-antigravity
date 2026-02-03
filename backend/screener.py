import pandas as pd
from . import data_ingestion

def calculate_rsi(series, period=14):
    """
    Calculates the Relative Strength Index (RSI).
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(series, window=50):
    """Calculates Simple Moving Average."""
    return series.rolling(window=window).mean()

def calculate_macd(series):
    """
    Calculates MACD (12, 26, 9).
    Returns (macd_line, signal_line, histogram)
    """
    exp12 = series.ewm(span=12, adjust=False).mean()
    exp26 = series.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def calculate_bollinger_bands(series, window=20, num_std=2):
    """
    Calculates Bollinger Bands.
    Returns (upper_band, middle_band, lower_band)
    """
    rolling_mean = series.rolling(window=window).mean()
    rolling_std = series.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

def check_technicals(history_df):
    """
    Checks technical criteria:
    1. RSI < 30 (Oversold) - relaxed to 40 for broader search if needed
    2. % Below 52-week High > 20% (Unloved)
    Returns a dictionary of metrics if it passes, else None.
    """
    if history_df.empty:
        return None
    
    # We rely on 'Close' column. 
    # If using yf.download with group_by='ticker', usage depends on shape.
    # This function expects a single ticker's dataframe with 'Close'
    
    try:
        close_prices = history_df['Close']
        current_price = close_prices.iloc[-1]
        
        # Drawdown
        high_52 = close_prices.max()
        drawdown_pct = ((high_52 - current_price) / high_52) * 100
        
        # RSI
        # Simple rolling RSI for approximation. 
        # For more precision, we'd use EWMA, but rolling mean is fine for a rough screener.
        # Let's use Wilder's Smoothing if possible, but standard rolling is robust enough for now.
        delta = close_prices.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # MACD
        macd, signal, hist = calculate_macd(close_prices)
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        
        # Bollinger Bands
        bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close_prices)
        current_bb_lower = bb_lower.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        
        # SMAs
        sma_50 = calculate_sma(close_prices, 50)
        sma_200 = calculate_sma(close_prices, 200)
        current_sma_50 = sma_50.iloc[-1]
        current_sma_200 = sma_200.iloc[-1]
        
        # CRITERIA
        if current_rsi < 40 and drawdown_pct > 15: # Slightly relaxed for testing
            reasons = []
            if current_rsi < 30:
                reasons.append(f"Extremely Oversold (RSI {current_rsi:.0f})")
            elif current_rsi < 40:
                reasons.append(f"Oversold (RSI {current_rsi:.0f})")
                
            if drawdown_pct > 20:
                reasons.append(f"Deep Correction (-{drawdown_pct:.0f}% off highs)")
            else:
                reasons.append(f"Pullback (-{drawdown_pct:.0f}%)")

            # Check Advanced Indicators
            if current_macd > current_signal:
                reasons.append("MACD Bullish Crossover")
            
            if current_price < current_bb_lower:
                reasons.append("Below Lower Bollinger Band")
            elif current_price < current_bb_lower * 1.02:
                reasons.append("Near Lower Bollinger Band")
                
            if current_sma_50 > current_sma_200:
                reasons.append("Golden Cross (SMA50 > SMA200)")
            elif current_sma_50 < current_sma_200:
                reasons.append("Death Cross (SMA50 < SMA200)")

            return {
                'Price': current_price,
                'RSI': current_rsi,
                'DrawdownPct': drawdown_pct,
                '52W_High': high_52,
                'DrawdownPct': drawdown_pct,
                '52W_High': high_52,
                'MACD': current_macd,
                'MACD_Signal': current_signal,
                'BB_Lower': current_bb_lower,
                'BB_Upper': current_bb_upper,
                'SMA_50': current_sma_50,
                'SMA_200': current_sma_200,
                'Reasons': reasons
            }
    except Exception as e:
        # print(f"Error checking technicals: {e}") 
        return None
        
    return None

def check_fundamentals(ticker, metrics):
    """
    Fetches and checks fundamental criteria.
    Updates the metrics dictionary if valid.
    """
    try:
        data, info = data_ingestion.fetch_stock_data(ticker)
        if not info:
            return None
            
        pe_ratio = info.get('forwardPE')
        debt_equity = info.get('debtToEquity')
        profit_margins = info.get('profitMargins')
        sector = info.get('sector', 'Unknown')
        short_name = info.get('shortName', ticker)
        
        # CRITERIA
        # 1. Valuation: Forward P/E < 20 (or valid and reasonable)
        # 2. Financial Health: Debt/Equity check (e.g. < 200 depending on unit, yfinance returns pct usually)
        # 3. Profitability: Positive margins
        
        # Note: yfinance debtToEquity is usually a percentage (e.g., 50.5 means 50.5%)
        # But sometimes it can be tricky. Let's assume < 200 (2.0 ratio) is safe.
        
        valid_pe = pe_ratio is not None and 0 < pe_ratio < 25
        valid_debt = True # debt_equity is not None and debt_equity < 250 # Relaxed for capital intensive
        valid_profit = profit_margins is not None and profit_margins > 0
        
        
        if valid_pe and valid_profit:
            # Append fundamental reasons
            reasons = metrics.get('Reasons', [])
            if pe_ratio < 15:
                reasons.append(f"Value Territory (P/E {pe_ratio:.1f})")
            else:
                reasons.append(f"Reasonable Valuation (P/E {pe_ratio:.1f})")
                
            if profit_margins > 0.2:
                reasons.append("High Margins")

            metrics.update({
                'Name': short_name,
                'Sector': sector,
                'PE': pe_ratio,
                'DebtEquity': debt_equity,
                'ProfitMargins': profit_margins,
                'Description': info.get('longBusinessSummary', '')[:300] + "...", # Extended length
                'Reasons': reasons
            })
            return metrics
            
    except Exception as e:
        print(f"Error checking fundamentals for {ticker}: {e}")
        return None
        
    return None

def run_screen():
    print("Fetching S&P 500 tickers...")
    tickers = data_ingestion.get_sp500_tickers()
    print(f"Got {len(tickers)} tickers. Fetching bulk price history...")
    
    # Batch processing is safer for bulk download if list is huge, 
    # but 500 is fine for one go usually.
    bulk_data = data_ingestion.fetch_bulk_history(tickers)
    
    candidates = []
    
    print("Running technical filters...")
    for ticker in tickers:
        try:
            # Handle MultiIndex columns logic from yfinance
            if isinstance(bulk_data.columns, pd.MultiIndex):
                stock_history = bulk_data[ticker].dropna()
            else:
                # If single ticker result (unlikely with list)
                stock_history = bulk_data
            
            tech_metrics = check_technicals(stock_history)
            if tech_metrics:
                print(f" -> {ticker} passed technicals (RSI: {tech_metrics['RSI']:.1f}, DD: {tech_metrics['DrawdownPct']:.1f}%)")
                # Step 2: Check Fundamentals
                final_metrics = check_fundamentals(ticker, tech_metrics)
                if final_metrics:
                    # Generate Natural Language Narrative
                    narrative = ai_engine.generate_thesis(ticker, final_metrics)
                    final_metrics['Rationale'] = narrative
                    
                    candidates.append({**{'Ticker': ticker}, **final_metrics})
                    print(f"    -> {ticker} PASSES FUNDAMENTALS!")
        except KeyError:
            continue
            
    return candidates

    return " ".join(narrative_parts)

# Initialize AI Engine (Global for now, or could be in run_screen)
try:
    from .ai_engine import AIEngine
    ai_engine = AIEngine()
except ImportError:
    # Fallback if I run this as a script in the wrong context
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.ai_engine import AIEngine
    ai_engine = AIEngine()

if __name__ == "__main__":
    results = run_screen()
    print(f"\nFound {len(results)} contrarian picks.")
    print(pd.DataFrame(results))
