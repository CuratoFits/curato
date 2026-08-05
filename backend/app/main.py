from fastapi import FastAPI

from app.api.routes import router as old_router
from app.api.product_routes import router as product_router


app = FastAPI(
    title="Curato Backend",
    version="1.0.0",
)


app.include_router(
    old_router,
    prefix="/api",
)

app.include_router(
    product_router,
    prefix="/api",
)


@app.get("/")
def health_check():
    return {
        "message": "Curato backend is running"
    }