from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from app.api.routes.products import products
from app.schemas.inventory import InventoryResponse, InventoryUpdateRequest


router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=list[InventoryResponse])
def list_inventory() -> list[InventoryResponse]:
    return [
        InventoryResponse(
            product_id=product.product_id,
            product_name=product.name,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )
        for product in products.values()
    ]


@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: UUID) -> InventoryResponse:
    product = products.get(product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return InventoryResponse(
        product_id=product.product_id,
        product_name=product.name,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
    )


@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: UUID, inventory_data: InventoryUpdateRequest) -> InventoryResponse:
    product = products.get(product_id)

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product.stock_quantity = inventory_data.stock_quantity

    return InventoryResponse(
        product_id=product.product_id,
        product_name=product.name,
        stock_quantity=product.stock_quantity,
        is_active=product.is_active,
    )