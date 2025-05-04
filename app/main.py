from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .auth.routes import router as auth_router
from .users.routes import router as users_router
from .tasks.routes import router as tasks_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Freelance Marketplace")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(tasks_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to Freelance Marketplace"}  