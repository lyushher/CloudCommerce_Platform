from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.inventory import InventoryResponse, InventoryUpdateRequest

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)) -> list[InventoryResponse]:
    statement = select(Product)
    products = db.scalars(statement).all()

    return [
        InventoryResponse(
            product_id=product.product_id,
            product_name=product.name,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )
        for product in products
    ]


@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: UUID, db: Session = Depends(get_db)) -> InventoryResponse:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return InventoryResponse(
        product_id=product.product_id,
        product_name=product.name,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
    )


@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: UUID, inventory_data: InventoryUpdateRequest, db: Session = Depends(get_db)) -> InventoryResponse:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product.stock_quantity = inventory_data.stock_quantity

    db.commit()
    db.refresh(product)

    return InventoryResponse(
        product_id=product.product_id,
        product_name=product.name,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
    )