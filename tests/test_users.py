from uuid import UUID
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password


def test_create_user(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/users",
        json={
            "email": "firdevs@example.com",
            "username": "firdevs",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "firdevs@example.com"
    assert data["username"] == "firdevs"
    assert data["is_active"] is True
    assert "user_id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data

    persisted_user = db_session.get(
        User,
        UUID(data["user_id"]),
    )

    assert persisted_user is not None
    assert persisted_user.email == "firdevs@example.com"
    assert persisted_user.username == "firdevs"
    assert persisted_user.hashed_password != "password123"

    assert verify_password("password123", persisted_user.hashed_password)

def test_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {
        "email": "firdevs@example.com",
        "username": "firdevs",
        "password": "password123",
    }

    first_response = client.post("/users", json=payload)
    second_response = client.post(
        "/users",
        json={
            **payload,
            "username": "another-user",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"

def test_duplicate_username_returns_409(client: TestClient) -> None:
    first_response = client.post(
        "/users",
        json={
            "email": "firdevs@example.com",
            "username": "firdevs",
            "password": "password123",
        },
    )

    second_response = client.post(
        "/users",
        json={
            "email": "another@example.com",
            "username": "firdevs",
            "password": "password123",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Username already registered"