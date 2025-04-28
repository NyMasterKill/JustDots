from fastapi import FastAPI
from .auth.routes import router as auth_router

app = FastAPI(title="Freelance Marketplace")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to Freelance Marketplace"}