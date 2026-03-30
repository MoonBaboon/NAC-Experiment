from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
import os
import redis

app = FastAPI()

r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Get DB credentials frrom environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = "db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)

@app.get("/")
def home():
    return {"message": "Hey"}

@app.get("/health")
def health():
    return {"status": "Up and running baby!"}

@app.get("/db-test")
def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            return {"status": "Success yay!"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DB connect error: {str(e)}"
        )

@app.get("/redis-test")
def test_redis():
    try:
        r.set("test_key", "Redis works yay!")
        value = r.get("test_key")
        return {"status": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
