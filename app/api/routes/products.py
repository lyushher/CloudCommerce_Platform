from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.products import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)

router = APIRouter(prefix="/products", tags=["Products"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreateRequest, db: DatabaseSession) -> Product:
    product = Product(
        name = product_data.name,
        description = product_data.description,
        price = product_data.price,
        stock_quantity = product_data.stock_quantity,
        category = product_data.category
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product



@router.get("", response_model=list[ProductResponse])
def list_products(db: DatabaseSession) -> list[Product]:
    statement = select(Product)
    products = db.scalars(statement).all()

    return list(products)



@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: DatabaseSession) -> Product:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product



@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, product_data: ProductUpdateRequest,
                    db: DatabaseSession) -> Product:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product



@router.delete( "/{product_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: DatabaseSession) -> None:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()