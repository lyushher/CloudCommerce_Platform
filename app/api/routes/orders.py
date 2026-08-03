from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.core.database import get_db
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.orders import OrderCreateRequest, OrderResponse, OrderStatus



router = APIRouter(prefix="/orders", tags=["Orders"])



@router.post("", response_model = OrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order_data: OrderCreateRequest, db: Session = Depends(get_db)) -> Order:
    validated_products: list[tuple[Product, int]] = []

    for item in order_data.items:
        product = db.get(Product, item.product_id)

        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {item.product_id} not found")
        
        if not product.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Product {product.name} is not active")
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Insufficient stock for {product.name}")
        
        validated_products.append((product, item.quantity))

    total_amount = sum(product.price * quantity
                        for product, quantity in validated_products)

    db_order = Order(customer_name=order_data.customer_name, total_amount=Decimal(total_amount),
                      status=OrderStatus.pending)

    
    for product, quantity in validated_products:
        product.stock_quantity -= quantity

        db_order.items.append(OrderItem(
            product_id = product.product_id,
            product_name = product.name,
            quantity = quantity,
            price = product.price
        ))

    db.add(db_order)

    try:
        db.commit()
        db.refresh(db_order)

    except Exception:
        db.rollback()
        raise

    return db_order


@router.get("", response_model = list[OrderResponse])
def list_orders(db: Session=Depends(get_db)) -> list[Order]:
    return(
        db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        .scalars()
        .all()
    )


@router.get("/{order_id}", response_model = OrderResponse)
def get_order(order_id: UUID,
              db: Session = Depends(get_db)) -> Order:
    order = (
        db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id)
        )
        .scalar_one_or_none()
    )

    if order is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Order not found")
    
    return order