from uuid import uuid4

from fastapi.testclient import TestClient



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



def test_list_orders_returns_persisted_orders(client: TestClient) -> None:
    product_response = client.post("/products", json={
            "name": "Mouse",
            "description": "Wireless Mouse",
            "category": "Accessories",
            "price": 49.99,
            "stock_quantity": 5,
    })

    assert product_response.status_code == 201
    product = product_response.json()

    create_response = client.post("/orders",json={
        "customer_name": "Firdevs",
        "items": [
            {
                "product_id": product["product_id"],
                "product_name": product["name"],
                "quantity": 1,
                "price": product["price"],
            }
        ],
    })

    assert create_response.status_code == 201
    created_order = create_response.json()

    response = client.get("/orders")

    assert response.status_code == 200

    orders = response.json()

    assert len(orders) == 1
    assert orders[0]["order_id"] == created_order["order_id"]
    assert orders[0]["customer_name"] == "Firdevs"
    assert orders[0]["items"][0]["product_id"] == product["product_id"]


def test_get_order_returns_persisted_order(client: TestClient) -> None:
    product_response = client.post(
        "/products",
        json={
            "name": "Monitor",
            "description": "27-inch monitor",
            "category": "Electronics",
            "price": 299.99,
            "stock_quantity": 3,
        },
    )

    assert product_response.status_code == 201
    product = product_response.json()

    create_response = client.post(
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

    assert create_response.status_code == 201
    created_order = create_response.json()

    response = client.get(f"/orders/{created_order['order_id']}")

    assert response.status_code == 200

    order = response.json()

    assert order["order_id"] == created_order["order_id"]
    assert order["customer_name"] == "Firdevs"
    assert order["total_amount"] == "299.99"
    assert order["items"][0]["product_name"] == "Monitor"


def test_get_missing_order_returns_404(client: TestClient) -> None:
    response = client.get(f"/orders/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"