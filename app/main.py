from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Launching the server...", flush=True)
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/hello")
def hello():
    return {"message": "HELLO :D"}
