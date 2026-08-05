from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.schemas.users import UserCreateRequest, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("", response_model= UserResponse,
             status_code=status.HTTP_201_CREATED)

def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db)) -> User:

    existing_user = (db.query(User)
        .filter(
            or_(
                User.email == user_data.email,
                User.username == user_data.username,
            )
        )
        .first()
    )

    if existing_user is not None:
        if existing_user.email == user_data.email:
            detail = "Email already registered"

        else:
            detail = "Username already registered"

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=detail)

    user = User(
        email=user_data.email,
        username = user_data.username,
        hashed_password = hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

