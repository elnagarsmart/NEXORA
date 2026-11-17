from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NEXORA API", version="0.1.0")

class Health(BaseModel):
    status: str
    app: str
    version: str

@app.get("/health", response_model=Health)
def health():
    return Health(status="ok", app="NEXORA", version="0.1.0")

@app.get("/")
def root():
    return {"name": "NEXORA", "message": "Smart Digital World API"}
