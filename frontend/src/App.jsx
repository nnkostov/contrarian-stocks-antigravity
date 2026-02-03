import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

function App() {
  const [favorites, setFavorites] = useState([])
  const [viewFavorites, setViewFavorites] = useState(false)
  const [loading, setLoading] = useState(false)
  const [candidates, setCandidates] = useState([])
  const [error, setError] = useState(null)

  // Fetch favorites on load
  useEffect(() => {
    fetchFavorites()
  }, [])

  const runScan = async () => {
    setLoading(true)
    setError(null)
    try {
      // In dev, we can point to localhost:18080
      const response = await axios.get('http://127.0.0.1:18080/api/scan')
      setCandidates(response.data.data)
    } catch (err) {
      console.error(err)
      setError('Failed to fetch data. Ensure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const fetchFavorites = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:18080/api/favorites')
      setFavorites(res.data)
    } catch (err) {
      console.error("Error fetching favorites:", err)
    }
  }

  const toggleFavorite = async (stock) => {
    const isFav = favorites.find(f => f.ticker === stock.Ticker)
    if (isFav) {
      // Remove
      try {
        await axios.delete(`http://127.0.0.1:18080/api/favorites/${stock.Ticker}`)
        setFavorites(favorites.filter(f => f.ticker !== stock.Ticker))
      } catch (err) {
        console.error("Error removing favorite:", err)
      }
    } else {
      // Add
      try {
        const payload = {
          ticker: stock.Ticker,
          name: stock.Name,
          sector: stock.Sector,
          price: stock.Price
        }
        const res = await axios.post('http://127.0.0.1:18080/api/favorites', payload)
        setFavorites([...favorites, res.data])
      } catch (err) {
        console.error("Error adding favorite:", err)
      }
    }
  }

  const isFavorite = (ticker) => favorites.some(f => f.ticker === ticker)

  // Combined list logic if we want to show favorites tab. 
  // For now, let's just mark them in the main list.

  return (
    <div className="container">
      <header>
        <h1>Contrarian Stock Picker</h1>
        <p>Uncovering unloved S&P 500 gems</p>
        <div className="stats">
          <span>Favorites: {favorites.length}</span>
        </div>
      </header>

      <main>
        <div className="actions">
          <button onClick={runScan} disabled={loading} className="primary-btn">
            {loading ? 'Scanning Market...' : 'Run Analysis'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {candidates.length > 0 && (
          <div className="results">
            <h2>Found {candidates.length} Opportunities</h2>
            <div className="stock-grid">
              {candidates.map((stock) => (
                <div key={stock.Ticker} className="stock-card">
                  <div className="card-header">
                    <div>
                      <span className="ticker-badge">{stock.Ticker}</span>
                      <span className="stock-name">{stock.Name}</span>
                    </div>
                    <div className="header-right">
                      <span className="stock-price">${stock.Price?.toFixed(2)}</span>
                      <button
                        className={`fav-btn ${isFavorite(stock.Ticker) ? 'active' : ''}`}
                        onClick={() => toggleFavorite(stock)}
                      >
                        {isFavorite(stock.Ticker) ? '★' : '☆'}
                      </button>
                    </div>
                  </div>

                  <div className="rationale-section">
                    <strong>Analysis</strong>
                    <p>{stock.Rationale || "Parameters met."}</p>
                  </div>

                  <div className="metrics-grid">
                    <div className="metric">
                      <label>RSI</label>
                      <span className={stock.RSI < 30 ? 'value-good' : ''}>{stock.RSI?.toFixed(1)}</span>
                    </div>
                    <div className="metric">
                      <label>Drawdown</label>
                      <span className="value-bad">-{stock.DrawdownPct?.toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <label>P/E</label>
                      <span>{stock.PE?.toFixed(1)}</span>
                    </div>
                    <div className="metric">
                      <label>Sector</label>
                      <span>{stock.Sector}</span>
                    </div>
                  </div>

                  {/* Advanced Technicals */}
                  <div className="advanced-metrics">
                    <div className="mini-metric">
                      <span>MACD:</span>
                      <span className={stock.MACD > (stock.MACD_Signal || 0) ? 'trend-up' : 'trend-down'}>
                        {stock.MACD > (stock.MACD_Signal || 0) ? 'Bullish' : 'Bearish'}
                      </span>
                    </div>
                    <div className="mini-metric">
                      <span>SMA Trend:</span>
                      <span className={stock.Price > (stock.SMA_200 || 99999) ? 'trend-up' : 'trend-down'}>
                        {stock.Price > (stock.SMA_200 || 99999) ? '> 200d' : '< 200d'}
                      </span>
                    </div>
                  </div>

                  <details className="business-summary">
                    <summary>Business Summary</summary>
                    <p>{stock.Description}</p>
                  </details>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
