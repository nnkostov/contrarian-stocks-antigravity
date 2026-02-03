from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from .database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    price_at_add = Column(Float, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
