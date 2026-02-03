from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel

from . import screener, data_ingestion, models
from .database import engine, get_db

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contrarian Stock Picker API")

# --- Pydantic Models ---
class StockResponse(BaseModel):
    Ticker: str
    Price: float
    RSI: float
    DrawdownPct: float
    PE: Optional[float] = None
    ProfitMargins: Optional[float] = None
    Sector: str
    Name: str
    Rationale: Optional[str] = None
    Description: Optional[str] = None
    MACD: Optional[float] = None
    MACD_Signal: Optional[float] = None
    BB_Lower: Optional[float] = None
    BB_Upper: Optional[float] = None
    SMA_50: Optional[float] = None
    SMA_200: Optional[float] = None

class ScanResponse(BaseModel):
    status: str
    count: int
    data: List[StockResponse]

class FavoriteCreate(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None

class FavoriteResponse(BaseModel):
    id: int
    ticker: str
    name: Optional[str]
    sector: Optional[str]
    price_at_add: Optional[float]
    added_at: Any # datetime

    class Config:
        from_attributes = True

# --- Middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serving Frontend (Must come after API routes) ---
# Check if dist folder exists (i.e. we are in Docker or built env)
if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    
    @app.get("/")
    async def serve_index():
        return FileResponse("frontend/dist/index.html")

# --- Endpoints ---

@app.get("/api/health")
def health_check():
    return {"status": "ok", "system": "Contrarian Stock Picker"}

@app.get("/api/scan", response_model=ScanResponse)
def run_scan():
    """
    Runs the screener and returns candidates.
    """
    try:
        candidates = screener.run_screen()
        return {"status": "success", "count": len(candidates), "data": candidates}
    except Exception as e:
        print(f"Error running scan: {e}")
        # Return empty list on error for now or raise
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/favorites", response_model=List[FavoriteResponse])
def get_favorites(db: Session = Depends(get_db)):
    favorites = db.query(models.Favorite).all()
    return favorites

@app.post("/api/favorites", status_code=status.HTTP_201_CREATED, response_model=FavoriteResponse)
def add_favorite(fav: FavoriteCreate, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(models.Favorite).filter(models.Favorite.ticker == fav.ticker).first()
    if existing:
        return existing
        
    db_fav = models.Favorite(
        ticker=fav.ticker,
        name=fav.name,
        sector=fav.sector,
        price_at_add=fav.price
    )
    db.add(db_fav)
    db.commit()
    db.refresh(db_fav)
    return db_fav

@app.delete("/api/favorites/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(ticker: str, db: Session = Depends(get_db)):
    existing = db.query(models.Favorite).filter(models.Favorite.ticker == ticker).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    db.delete(existing)
    db.commit()
    return
