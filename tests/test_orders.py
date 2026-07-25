from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.products import products
from app.api.routes.orders import orders
from uuid import uuid4, UUID


client = TestClient(app)


def setup_function():
    products.clear()
    orders.clear()

def test_create_order():
    product_response = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "category": "Accessories",
        "price": 89.99,
        "stock_quantity": 10,
        "is_active": True,
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
    inventory_data = inventory_response.json()
    assert inventory_data["stock_quantity"] == 8



from uuid import uuid4


def test_create_order_with_missing_product_returns_404():
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


def test_create_order_with_insufficient_stock_returns_409():
    product_response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "category": "Accessories",
            "price": 89.99,
            "stock_quantity": 1,
            "is_active": True,
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


def test_create_order_with_inactive_product_returns_400():
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

    product_id = UUID(product["product_id"])
    products[product_id].is_active = False

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