from fastapi import FastAPI

from app.api.routes import router as old_router
from app.api.product_routes import router as product_router
from app.api.user_profile_routes import router as user_profile_router
from app.api.interaction_routes import router as interaction_router


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


app.include_router(
    user_profile_router,
    prefix="/api",
)

app.include_router(
    interaction_router,
    prefix="/api",
)

@app.get("/")
def health_check():
    return {
        "message": "Curato backend is running"
    }