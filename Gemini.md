# Contrarian Stock Picker - Development & Architecture Notes

## Project Overview
This project is an agentic AI-developed system designed to identify "Contrarian" stock picks from the S&P 500. It targets stocks that are statistically "unloved" (oversold, high drawdown) but possess strong fundamentals.

## Architecture

The system operates as a hybrid application: it can be run as a standalone CLI script or as a full-stack web application.

### 1. Data Layer
*   **S&P 500 Constituents**: Fetched from a public [GitHub Dataset](https://github.com/datasets/s-and-p-500-companies) (CSV).
*   **Market Data**: Uses `yfinance` to fetch 1-year history (price, volume) and fundamentals (P/E, Margins).

### 2. Core Logic (`backend/`)
*   **`data_ingestion.py`**: Handles reliable fetching of the stock list and bulk price history (threaded).
*   **`screener.py`**: The mathematical engine.
    *   *Technicals*: RSI < 40, Drawdown > 15%.
    *   *Fundamentals*: P/E < 25, Positive Margins.

### 3. Application Layer
*   **CLI Mode (`main.py`)**: Direct python script execution.
*   **Web Mode**:
    *   **Backend (`backend/api.py`)**: **FastAPI** server running on **Port 18080**.
    *   **Frontend (`frontend/`)**: **React (Vite)** SPA running on **Port 15173**.
    *   ORCHESTRATION: Managed by `./run_app.sh`.

## Development History & Key Decisions

### Phase 1: MVP (CLI)
*   **Solution**: Switched from scraping Wikipedia to static CSV for S&P 500 list reliability. Implemented `yfinance` bulk download.

### Phase 2: Web Interface
*   **Refactoring**: Modularized code into `backend` package with relative imports.
*   **Tech Stack**: FastAPI + React + Vanilla CSS (Dark Mode).

### Phase 3: Configuration Updates
*   **Ports**: Migrated from standard ports (8000/5173) to **unusual ports (18080/15173)** to avoid local conflicts.

## Future Updates (Roadmap)
These are discussed features not yet implemented:

1.  **AI/LLM Integration**:
    *   Summarize news headlines for "Why is this stock down?".
    *   Analyze 10-K "Risk Factors" sections.
2.  **Advanced Technicals**:
    *   Add MACD, Bollinger Bands, and Moving Average Crossovers (Golden Cross).
3.  **Persistence**:
    *   Add a SQLite database to save "Favorite" picks or track screen results over time.
4.  **Deployment**:
    *   Dockerize the application for easy deployment to cloud services (Render/Railway).
