from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.orders import OrderCreateRequest, OrderResponse, OrderStatus

router = APIRouter(prefix="/orders", tags=["Orders"])

orders: dict[UUID, OrderResponse] = {}



@router.post("", response_model = OrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order_data: OrderCreateRequest, db: Session = Depends(get_db)) -> OrderResponse:
    validated_products = []

    for item in order_data.items:
        product = db.get(Product, item.product_id)

        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
        
        if not product.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Product {product.name} is not active")
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Insufficient stock for {product.name}")
        
        validated_products.append((product, item.quantity))

    
    for product, quantity in validated_products:
        product.stock_quantity -= quantity

    db.commit()
    
    total_amount = sum(
        item.price * item.quantity
        for item in order_data.items
    )

    order = OrderResponse(
        order_id=uuid4(),
        customer_name = order_data.customer_name,
        items= order_data.items,
        total_amount= Decimal(total_amount),
        status = OrderStatus.pending,
        created_at= datetime.now(UTC),
    )

    orders[order.order_id] = order

    return order


@router.get("", response_model = list[OrderResponse])
def list_orders() -> list[OrderResponse]:
    return list(orders.values())


@router.get("/{order_id}", response_model = OrderResponse)
def get_order(order_id: UUID) -> OrderResponse:
    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Order not found")
    
    return order