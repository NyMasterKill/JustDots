from fastapi import FastAPI
from .auth.routes import router as auth_router
from tasks.routes import router as tasks_router


app = FastAPI(title="Freelance Marketplace")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
async def root():
    return {"message": "Welcome to Freelance Marketplace"}