from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock_quantity: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=100)


class ProductResponse(BaseModel):
    product_id: UUID
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    category: str
    is_active: bool
    created_at: datetime

    