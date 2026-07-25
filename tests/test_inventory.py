from fastapi.testclient import TestClient
from app.api.routes.products import products
from app.main import app


client = TestClient(app)

def setup_function() -> None:
    products.clear()

def create_test_product() -> dict:
    response = client.post("/products", json={
        "name": "Test Laptop",
        "description": "Laptop created for inventory tests",
        "price": "1200.00",
        "stock_quantity": 10,
        "category": "Electronics",
    })

    assert response.status_code == 201
    return response.json()

def test_list_inventory() -> None:
    product = create_test_product()

    response = client.get("/inventory")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1 
    assert data[0]["product_id"] == product["product_id"]
    assert data[0]["product_name"] == "Test Laptop"
    assert data[0]["stock_quantity"] == 10
    assert data[0]["is_active"] is True


def test_get_inventory_by_product_id() -> None:
    product = create_test_product()

    response = client.get(f"/inventory/{product['product_id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product["product_id"]
    assert data["product_name"] == "Test Laptop"
    assert data["stock_quantity"] == 10
    assert data["is_active"] is True


def test_update_inventory() -> None:
    product = create_test_product()

    response = client.put(f"/inventory/{product['product_id']}", json={"stock_quantity": 50})

    assert response.status_code ==200

    data = response.json()

    assert data["product_id"] == product["product_id"]
    assert data["stock_quantity"] == 50


def test_negative_stock_is_rejected() -> None:
    product = create_test_product()

    response = client.put(f"/inventory/{product['product_id']}", json={"stock_quantity": -1})

    assert response.status_code == 422


def test_missing_product_returns_404() -> None:
    response = client.get("/inventory/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}