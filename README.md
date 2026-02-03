# Contrarian Stock Picker (S&P 500)

A Python-based agentic system that identifies "unloved" stocks with high upside potential from the S&P 500.

## Logic
The screener applies a two-stage filter:

1.  **Technical Filter (The "Unloved" Signal)**
    *   **RSI (14-day)**: < 40 (Oversold/Weak momentum)
    *   **Drawdown**: > 15% from 52-week High

2.  **Fundamental Filter (The "Quality" Check)**
    *   **Forward P/E**: 0 < P/E < 25 (Valuation check)
    *   **Profit Margins**: > 0 (Must be profitable)
    *   **Debt/Equity**: Checked for excessive leverage (via logic in `screener.py`)

## Usage

### Option 1: Web Dashboard (Recommended)
The easiest way to use the tool is via the orchestration script, which launches both the API and the UI.
```bash
./run_app.sh
```
*   Opens the dashboard at `http://localhost:15173`.
*   Backend runs on `http://127.0.0.1:18080`.

### Option 2: CLI Report
To generate a static Markdown report without the web UI:
```bash
# Sourcing venv if needed
source venv/bin/activate
python main.py
```
This generates `contrarian_report.md`.

## Project Structure
*   `backend/`: Core logic and API.
    *   `api.py`: FastAPI server.
    *   `screener.py`: Screening algorithms (RSI, Drawdown).
    *   `data_ingestion.py`: Data fetching (S&P 500, yfinance).
*   `frontend/`: React application (Vite).
*   `main.py`: CLI entry point.
*   `run_app.sh`: Helper script to launch the full stack.

## Documentation
See [Gemini.md](Gemini.md) for detailed architecture notes and future roadmap.
