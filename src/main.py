from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.routes import router as auth_router
from src.orders.routes import router as orders_router
from src.order_responses.routes import router as order_responses_router
from src.reviews.routes import router as reviews_router
from src.websocket.routes import router as ws_router
from src.categories.routes import router as categories_router
# from src.roles.routes import router as roles_router
# from src.skills.routes import router as skills_router
# from src.user_skills.routes import router as user_skills_router
# from src.user_portfolio.routes import router as user_portfolio_router
from src.database import Base, engine

app = FastAPI(
    title="Freelance Marketplace",
    description="A platform for freelancers and clients to collaborate on projects.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(order_responses_router)
app.include_router(reviews_router)
app.include_router(ws_router)
app.include_router(categories_router)
# app.include_router(roles_router)
# app.include_router(skills_router)
# app.include_router(user_skills_router)
# app.include_router(user_portfolio_router)