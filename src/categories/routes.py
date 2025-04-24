from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.categories.models import Category
from src.categories.schemas import Category, CategoryBase

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=Category)
def create_category(category: CategoryBase, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()