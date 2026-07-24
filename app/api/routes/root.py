from fastapi import APIRouter
from app.core.config import settings
from app.schemas.responses import RootResponse


router = APIRouter()

@router.get("/", response_model = RootResponse)
def root() -> RootResponse:
    return RootResponse(
        name = settings.app_name,
        version = settings.app_version,
        environment = settings.environment,
        status="running",
    )