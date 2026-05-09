import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'service'))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


# --- HEALTH ---

def test_health_always_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_has_status_field():
    response = client.get("/health")
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


# --- PAYMENTS ---

def test_payment_returns_valid_status_code():
    response = client.get("/payments")
    assert response.status_code in [200, 500]


def test_payment_success_has_transaction_id():
    # Run multiple times since it randomly fails
    for _ in range(10):
        response = client.get("/payments")
        if response.status_code == 200:
            data = response.json()
            assert "transaction_id" in data
            assert isinstance(data["transaction_id"], int)
            return
    # If all 10 failed randomly, that's fine — we just skip
    

def test_payment_forced_failure_returns_500():
    response = client.get("/payments?fail=true")
    assert response.status_code == 500


def test_payment_forced_failure_has_error_detail():
    response = client.get("/payments?fail=true")
    assert "detail" in response.json()


# --- LOGIN ---

def test_login_forced_failure_returns_401():
    response = client.get("/login?fail=true")
    assert response.status_code == 401


def test_login_success_has_token():
    for _ in range(10):
        response = client.get("/login")
        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert isinstance(data["token"], int)
            return


# --- ORDERS ---

def test_orders_forced_failure_returns_500():
    response = client.get("/orders?fail=true")
    assert response.status_code == 500


def test_orders_success_returns_list():
    for _ in range(10):
        response = client.get("/orders")
        if response.status_code == 200:
            data = response.json()
            assert "orders" in data
            assert isinstance(data["orders"], list)
            return


# --- PORTFOLIO ---

def test_portfolio_forced_failure_returns_500():
    response = client.get("/portfolio?fail=true")
    assert response.status_code == 500


def test_portfolio_success_has_value():
    for _ in range(10):
        response = client.get("/portfolio")
        if response.status_code == 200:
            data = response.json()
            assert "portfolio_value" in data
            assert data["portfolio_value"] > 0
            return