from fastapi import FastAPI
from app.db.connection import get_db


app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "HELLO :D"}
