from fastapi import FastAPI
from app.db.connection import get_db
from app.api.routes.components import router as components_router
from app.api.routes.measurements import router as measurements_router
from app.api.routes.auth import router as auth_router
from app.api.routes.reports import router as reports_router

app = FastAPI()
app.include_router(components_router)
app.include_router(measurements_router)
app.include_router(auth_router)
app.include_router(reports_router)


@app.get("/hello")
def hello():
    return {"message": "HELLO :D, visit /docs to see all the documentation"}
