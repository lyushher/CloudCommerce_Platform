from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order():
    response = client.post("/orders", json={
        "customer_name": "Firdevs",
        "items" : [{
            "product_name": "Keyboard",
            "quantity": 2,
            "price": 89.99,
        }],
    })

    assert response.status_code == 201

    data = response.json()

    assert data["customer_name"] == "Firdevs"
    assert data["status"] == "PENDING"
    assert data["total_amount"] == "179.98"
    assert "order_id" in data