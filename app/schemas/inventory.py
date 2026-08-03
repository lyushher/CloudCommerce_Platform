from uuid import UUID

from pydantic import BaseModel, Field


class InventoryUpdateRequest(BaseModel):
    stock_quantity: int = Field(ge=0)    

class InventoryResponse(BaseModel):
    product_id: UUID
    product_name: str
    stock_quantity: int
    is_active: bool

