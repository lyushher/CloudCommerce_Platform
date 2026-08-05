from fastapi import APIRouter

from app.api.routes import(health, inventory,
                            orders, products, root, users, auth)

api_router = APIRouter()

api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(orders.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(users.router)
api_router.include_router(auth.router)