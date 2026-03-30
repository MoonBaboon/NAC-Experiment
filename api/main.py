from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hey"}

@app.get("/health")
def health():
    return {"status": "Up and running baby!"}
