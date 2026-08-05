import jwt
from fastapi.testclient import TestClient
from app.core.config import settings
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user import User



def create_test_user(client: TestClient) -> dict:
    response = client.post(
        "/users",
        json={
            "email": "firdevs@example.com",
            "username": "firdevs",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_login_returns_access_token(client: TestClient) -> None:
    user = create_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "firdevs@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert "access_token" in data

    payload = jwt.decode(
        data["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == user["user_id"]
    assert "exp" in payload


def test_login_with_invalid_password_returns_401(
    client: TestClient,
) -> None:
    create_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "firdevs@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_with_unknown_email_returns_401(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "missing@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_inactive_user_cannot_login(
    client: TestClient,
    db_session: Session,
) -> None:
    user_data = create_test_user(client)

    user = db_session.get(
        User,
        UUID(user_data["user_id"]),
    )

    assert user is not None

    user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "firdevs@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user"