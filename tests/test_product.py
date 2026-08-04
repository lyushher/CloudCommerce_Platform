from fastapi.testclient import TestClient
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.product import Product
from decimal import Decimal



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



def test_create_product_is_persisted(
        client: TestClient,
        db_session: Session) -> None:
    
    response = client.post("/products", json={
        "name": "Database Keyboard",
        "description": "Product persistence test",
        "price": "99.99",
        "stock_quantity": 15,
        "category": "Electronics",
    })

    assert response.status_code == 201

    product_id = UUID(response.json()["product_id"])

    persisted_product = db_session.get(Product, product_id)

    assert persisted_product is not None
    assert persisted_product.name == "Database Keyboard"
    assert persisted_product.price == Decimal("99.99")
    assert persisted_product.stock_quantity == 15