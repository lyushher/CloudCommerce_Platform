from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status
from app.schemas.products import ProductCreateRequest, ProductResponse


router = APIRouter(prefix="/products", tags=["Products"])
products: dict[UUID, ProductResponse] = {}

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreateRequest) -> ProductResponse:
    product = ProductResponse(
        product_id = uuid4(),
        name = product_data.name,
        description = product_data.description,
        price = product_data.price,
        stock_quantity = product_data.stock_quantity,
        category = product_data.category,
        is_active = True,
        created_at = datetime.now(timezone.utc),
    )

    products[product.product_id] = product

    return product


@router.get("", response_model = list[ProductResponse])
def list_products() -> list[ProductResponse]:
    return list(products.values())


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID) -> ProductResponse:
    product = products.get(product_id)

    if product is None:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return product