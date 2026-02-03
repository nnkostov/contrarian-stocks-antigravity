from fastapi.testclient import TestClient
from backend.api import app
from backend.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_favorites_flow():
    # 1. Clean verify
    # (Optional: drop tables or file)
    
    # 2. Add Favorite
    payload = {
        "ticker": "TEST",
        "name": "Test Company",
        "sector": "Technology",
        "price": 100.0
    }
    response = client.post("/api/favorites", json=payload)
    if response.status_code != 201:
        print(f"FAILED POST: {response.text}")
        return
        
    data = response.json()
    print(f"Added Favorite: {data['ticker']} (ID: {data['id']})")
    
    # 3. Get Favorites
    response = client.get("/api/favorites")
    favorites = response.json()
    print(f"Favorites count: {len(favorites)}")
    found = any(f['ticker'] == 'TEST' for f in favorites)
    if not found:
        print("FAILED: Did not find TEST in favorites list.")
        return
        
    # 4. Delete Favorite
    response = client.delete("/api/favorites/TEST")
    if response.status_code != 204:
        print(f"FAILED DELETE: {response.status_code}")
        return
        
    print("Deleted Favorite.")
    
    # 5. Verify Empty
    response = client.get("/api/favorites")
    if any(f['ticker'] == 'TEST' for f in response.json()):
        print("FAILED: TEST still exists after delete.")
    else:
        print("SUCCESS: Full Favorites flow verified.")

if __name__ == "__main__":
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    test_favorites_flow()
    if os.path.exists("./test.db"):
        os.remove("./test.db")
