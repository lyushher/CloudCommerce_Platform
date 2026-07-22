from fastapi import FastAPI
from app.core.config import settings
from app.schemas.responses import HealthResponse, RootResponse


app = FastAPI(
    title=settings.app_name,
    description=("A cloud-native backend platform for reliable and asynchronous order processing."),
    version=settings.app_version,
    debug= settings.debug,
)

@app.get("/", response_model = RootResponse)
def root() -> RootResponse:
    return RootResponse(
        name= settings.app_name,
        version= settings.app_version,
        environment= settings.environment,
        status= "running",
    )

@app.get("/health", response_model= HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status= "healthy",
    )