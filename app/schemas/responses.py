from pydantic import BaseModel


class RootResponse(BaseModel):
    name: str
    version: str
    environment: str
    status: str


class HealthResponse(BaseModel):
    status:str