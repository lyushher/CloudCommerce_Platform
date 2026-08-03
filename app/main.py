from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=("A cloud-native backend platform for reliable and asynchronous order processing."),
    version=settings.app_version,
    debug= settings.debug,
)

app.include_router(api_router)