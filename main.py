from fastapi import FastAPI

app = FastAPI(title="FlyRank Task Manager API")

@app.get("/")
def read_root():
    return {"message": "Hello, server"}
