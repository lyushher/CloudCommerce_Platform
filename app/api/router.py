from fastapi import APIRouter
from app.api.routes import health, orders, root, products

api_router = APIRouter()

api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(orders.router)
api_router.include_router(products.router)