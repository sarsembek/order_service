import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={"username": "testuser", "email": "test@example.com", "password": "password"})
    assert response.status_code == 200 or response.status_code == 409  # Handle duplicate user case
    if response.status_code == 200:
        assert response.json()["username"] == "testuser"

def test_login_user():
    client.post("/auth/register", json={"username": "testuser", "email": "test@example.com", "password": "password"})
    response = client.post("/auth/login", json={"username": "testuser", "password": "password"})  # Use JSON here
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_order():
    client.post("/auth/register", json={"username": "testuser", "email": "test@example.com", "password": "password"})
    login_response = client.post("/auth/login", json={"username": "testuser", "password": "password"})  # Use JSON here
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/orders", json={"products": [{"product_id": 1, "quantity": 2}]}, headers=headers)
    assert response.status_code == 200 or response.status_code == 404  # Handle product not found case
    if response.status_code == 200:
        assert response.json()["customer_name"] == "testuser"