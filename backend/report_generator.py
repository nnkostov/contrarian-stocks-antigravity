import pandas as pd
from datetime import datetime

def generate_markdown_report(candidates, filename="contrarian_report.md"):
    """
    Generates a Markdown report from the list of candidate dictionaries.
    """
    if not candidates:
        content = "# Contrarian Stock Report\n\nNo stocks found matching the criteria this time."
        with open(filename, 'w') as f:
            f.write(content)
        return filename

    # Sort candidates by RSI (lowest first) as a default rank
    # or by Drawdown (highest first)
    # Let's sort by RSI ascending (most oversold)
    candidates.sort(key=lambda x: x.get('RSI', 100))

    content = f"# Contrarian S&P 500 Stock Report\n"
    content += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    content += "The following stocks are mathematically 'unloved' (High Drawdown, Low RSI) "
    content += "but show potential fundamental quality (P/E, Margins).\n\n"
    
    content += "## Top Candidates\n\n"
    
    for stock in candidates:
        ticker = stock['Ticker']
        name = stock.get('Name', 'N/A')
        sector = stock.get('Sector', 'N/A')
        price = stock.get('Price', 0)
        rsi = stock.get('RSI', 0)
        dd = stock.get('DrawdownPct', 0)
        pe = stock.get('PE', 'N/A')
        
        content += f"### {ticker} - {name}\n"
        content += f"- **Sector:** {sector}\n"
        content += f"- **Price:** ${price:.2f}\n"
        content += f"- **Technical Signal:** RSI {rsi:.1f} | Drawdown -{dd:.1f}%\n"
        content += f"  - *MACD:* {'Bullish' if stock.get('MACD', 0) > stock.get('MACD_Signal', 0) else 'Bearish'}\n"
        content += f"  - *SMA Trend:* {'Above' if price > stock.get('SMA_200', 999999) else 'Below'} 200-day\n"
        content += f"- **Fundamentals:** Forward P/E {pe} | Margins {stock.get('ProfitMargins', 0)//1:.1%}\n"
        content += f"\n**Analysis:**\n> {stock.get('Rationale', 'No rationale available')}\n"
        content += f"\n**Business Description:**\n> {stock.get('Description', 'No description available')}\n\n"
        content += "---\n"
        
    # Summary Table
    content += "## Summary Table\n\n"
    df = pd.DataFrame(candidates)
    if not df.empty:
        # Select key columns
        cols = ['Ticker', 'Price', 'RSI', 'DrawdownPct', 'PE', 'Sector']
        summary_df = df[cols].copy()
        summary_df['Price'] = summary_df['Price'].round(2)
        summary_df['RSI'] = summary_df['RSI'].round(1)
        summary_df['DrawdownPct'] = summary_df['DrawdownPct'].round(1)
        
        content += summary_df.to_markdown(index=False)
    
    with open(filename, 'w') as f:
        f.write(content)
        
    return filename
