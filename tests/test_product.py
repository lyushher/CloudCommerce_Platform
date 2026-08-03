from fastapi.testclient import TestClient


def test_create_product(client: TestClient) -> None:
    response = client.post("/products", json={
        "name": "Mechanical Keyboard",
        "description": "Wireless mechanical keyboard",
        "price": "89.99",
        "stock_quantity": 25,
        "category": "Electronics",
        }
    )

    assert response.status_code ==201

    data = response.json()

    assert data["name"] == "Mechanical Keyboard"
    assert data["price"] == "89.99"
    assert data["stock_quantity"] == 25
    assert data["category"] == "Electronics"
    assert data["is_active"] is True
    assert "product_id" in data
    assert "created_at" in data




def test_get_product_by_id(client: TestClient) -> None:
    create_response = client.post("/products", json={
        "name": "Laptop",
        "description": "Developer laptop",
        "price": "1499.99",
        "stock_quantity": 10,
        "category": "Computers",
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["product_id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["product_id"] == product_id
    assert response.json()["name"] == "Laptop"