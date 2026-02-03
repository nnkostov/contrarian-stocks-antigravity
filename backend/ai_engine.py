import os
import google.generativeai as genai
from typing import Dict, Optional

class AIEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        # DEBUG LOGGING
        print(f"DEBUG: AIEngine initializing. Key type: {type(self.api_key)}")
        if self.api_key:
            print(f"DEBUG: Key found (length: {len(self.api_key)}). Configuring GenAI...")
        else:
            print("DEBUG: No API Key found in environment variables.")

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-3-pro-preview')
                print("DEBUG: Gemini model initialized successfully (Gemini 3 Pro).")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API: {e}")
    
    def generate_thesis(self, ticker: str, metrics: Dict, news_context: Optional[str] = None) -> str:
        """
        Generates a contrarian investment thesis for the given stock.
        If no API key is available, falls back to a template-based response.
        """
        if not self.model:
            return self._fallback_narrative(ticker, metrics)

        prompt = self._construct_prompt(ticker, metrics, news_context)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating AI narrative for {ticker}: {e}")
            return self._fallback_narrative(ticker, metrics)

    def _construct_prompt(self, ticker: str, metrics: Dict, news_context: Optional[str]) -> str:
        rsi = metrics.get('RSI', 'N/A')
        drawdown = metrics.get('DrawdownPct', 'N/A')
        pe = metrics.get('PE', 'N/A')
        margins = metrics.get('ProfitMargins', 'N/A')
        sector = metrics.get('Sector', 'Unknown Sector')
        
        lines = [
            f"You are a sophisticated contrarian value investor. Analyze {ticker} ({sector}) which has been flagged as a potential opportunity.",
            f"Key Metrics:",
            f"- It is down {drawdown:.1f}% from its 52-week high.",
            f"- RSI is {rsi:.1f} (Indicating oversold conditions)." if isinstance(rsi, (int, float)) else f"- RSI: {rsi}",
            f"- Forward P/E is {pe:.1f} (Valuation)." if isinstance(pe, (int, float)) else f"- P/E: {pe}",
            f"- Profit Margins are {margins:.1%}." if isinstance(margins, (int, float)) else f"- Margins: {margins}",
            f"- MACD is {'positive' if metrics.get('MACD', 0) > metrics.get('MACD_Signal', 0) else 'negative'} (Momentum).",
            f"- Price vs SMA: {'Above' if metrics.get('Price', 0) > metrics.get('SMA_200', 999999) else 'Below'} 200-day SMA.",
            f"- Bollinger Bands: {'Price is below lower band (Volatility extremes)' if metrics.get('Price', 0) < metrics.get('BB_Lower', -1) else 'Within bands'}.",
            "",
            "Write a concise, 3-sentence investment thesis.",
            "1. Explain the context of the drop (using RSI, Drawdown, and Moving Averages).",
            "2. Highlight the value proposition (Fundamentals).",
            "3. Note a technical nuance (MACD or Bollinger Bands) or risk.",
            "Output ONLY the thesis paragraph. Do not use markdown formatting like bolding."
        ]
        
        return "\n".join(lines)

    def _fallback_narrative(self, ticker: str, metrics: Dict) -> str:
        """
        Original template logic, preserved as fallback.
        """
        rsi = metrics.get('RSI', 50)
        drawdown = metrics.get('DrawdownPct', 0)
        pe = metrics.get('PE', 0)
        margins = metrics.get('ProfitMargins', 0)
        
        # Simple formatting logic
        if isinstance(margins, (int, float)):
             margins_str = f"{margins*100:.0f}%"
        else:
             margins_str = "N/A"

        return (
            f"[AI UNAVAILABLE - FALLBACK] {ticker} has fallen {drawdown:.0f}% from highs. "
            f"with an RSI of {rsi:.0f}, it appears oversold. "
            f"Trading at {pe:.1f}x forward earnings with {margins_str} margins."
        )
