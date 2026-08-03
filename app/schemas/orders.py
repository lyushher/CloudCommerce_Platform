from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    pending = "PENDING"
    processing = "PROCESSING"
    completed = "COMPLETED"
    cancelled = "CANCELLED"


class OrderItem(BaseModel):
    product_id: UUID
    product_name: str= Field(min_length=1, max_length=150)
    quantity: int = Field(gt=0)
    price: Decimal = Field(gt=0, decimal_places=2)

class OrderCreateRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    items: list[OrderItem] = Field(min_length=1)

class OrderResponse(BaseModel):
    order_id: UUID
    customer_name: str
    items: list[OrderItem]
    total_amount: Decimal
    status: OrderStatus
    created_at:datetime

