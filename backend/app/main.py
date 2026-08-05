from fastapi import FastAPI

from .api.routes import router
from .connections.connection import initialize_database

app = FastAPI(title="Curato Backend", version="1.0.0")
app.include_router(router, prefix="/api")

initialize_database()


@app.get("/")
def health_check():
    return {"message": "Curato backend is running"}
