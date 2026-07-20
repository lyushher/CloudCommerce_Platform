from fastapi import FastAPI

app = FastAPI(
    title="CloudCommerce Platform",
    description=("A cloud-native backend platform for reliable and asynchronous order processing."),
    version="0.1.0",
)

@app.get("/")
def root() -> dict[str, str]:
    return{
        "name": "CloudCommerce Platform",
        "version": "0.1.0",
        "status": "running",
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }