from fastapi import APIRouter
from app.schemas.responses import HealthResponse


router = APIRouter()

@router.get("/health", response_model = HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")