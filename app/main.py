from fastapi import FastAPI
from app.db.connection import get_db
from app.api.routes.components import router as components_router
from app.api.routes.measurements import router as measurements_router
from app.api.routes.auth import router as auth_router

app = FastAPI()
app.include_router(components_router)
app.include_router(measurements_router)
app.include_router(auth_router)


@app.get("/hello")
def hello():
    return {"message": "HELLO :D"}
