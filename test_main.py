import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
import models
from database import get_db, Base
import pdb
import os
from random import random

# Setup testing database with SQLite
engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'), connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database schema for testing
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
    
@pytest.fixture
def user():
    return models.User(username=f"carlos{random()}", email=f"carlos{random()}@mail.com", full_name="Carlos Gomez", password="password1234")

@pytest.fixture
def users(db, user):
    def _users(n):
        users = [user for i in range(n)]
        db.add_all(users)
        db.commit()
        return users
    return _users



def test_create_user(db, users):
    # print("Testing create user")
    # assert True
    
    users(3)

    response = client.post(
        "/users/"
    )
    print(response.status_code)
    print(response.json())
    
    # pdb.set_trace()
    
    assert response.status_code == 200
    data = response.json()
    assert data[0]["username"] == "carlos"
    assert "id" in data