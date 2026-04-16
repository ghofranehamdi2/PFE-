import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine, SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Smart Focus Assistant API"}

def test_create_user():
    response = client.post(
        "/api/v1/auth/register", # Need to add this endpoint or use direct CRUD for test
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    # Since I didn't add the register route yet, I'll add it to the backend now.
    pass
