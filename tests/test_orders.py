from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.routes.orders import orders


def setup_function() -> None :
    orders.clear()

def test_create_order(client: TestClient) -> None:
    product_response = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "category": "Accessories",
        "price": 89.99,
        "stock_quantity": 10,
    })

    assert product_response.status_code == 201

    product = product_response.json()   

    response = client.post("/orders", json={
        "customer_name": "Firdevs",
        "items" : [{
            "product_id": product["product_id"],
            "product_name": product["name"],
            "quantity": 2,
            "price": product["price"],
        }],
    })

    assert response.status_code == 201

    data = response.json()

    assert data["customer_name"] == "Firdevs"
    assert data["total_amount"] == "179.98"
    assert data["status"] == "PENDING"

    inventory_response = client.get(f"/inventory/{product['product_id']}")

    assert inventory_response.status_code == 200
    assert inventory_response.json()["stock_quantity"] == 8



def test_create_order_with_missing_product_returns_404(client: TestClient) -> None:
    response = client.post(
        "/orders",
        json={
            "customer_name": "Firdevs",
            "items": [
                {
                    "product_id": str(uuid4()),
                    "product_name": "Keyboard",
                    "quantity": 1,
                    "price": 89.99,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_order_with_insufficient_stock_returns_409(client: TestClient) -> None:
    product_response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "category": "Accessories",
            "price": 89.99,
            "stock_quantity": 1,
        },
    )

    assert product_response.status_code == 201
    product = product_response.json()

    response = client.post(
        "/orders",
        json={
            "customer_name": "Firdevs",
            "items": [
                {
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "quantity": 2,
                    "price": product["price"],
                }
            ],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient stock for Keyboard"


def test_create_order_with_inactive_product_returns_400(client: TestClient) -> None:
    product_response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "category": "Accessories",
            "price": 89.99,
            "stock_quantity": 10,
        },
    )

    assert product_response.status_code == 201
    product = product_response.json()

    update_response = client.put(f"/products/{product['product_id']}", json={"is_active": False})

    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False

    
    response = client.post(
        "/orders",
        json={
            "customer_name": "Firdevs",
            "items": [
                {
                    "product_id": product["product_id"],
                    "product_name": product["name"],
                    "quantity": 1,
                    "price": product["price"],
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Product Keyboard is not active"