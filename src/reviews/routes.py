from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.reviews.models import Review
from src.reviews.schemas import ReviewCreate, Review
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.orders.models import Order, OrderStatus
from src.auth.utils import recalculate_user_rating

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=Review)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(
        Order.id == review.order_id,
        Order.status == OrderStatus.CLOSED
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found or not closed")
    is_customer = (db_order.customer_id == current_user.id)
    is_executor = (db_order.executor_id == current_user.id)
    if not (is_customer or is_executor):
        raise HTTPException(status_code=403, detail="Not authorized to review this order")
    if review.target_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot review yourself")
    if review.target_id not in [db_order.customer_id, db_order.executor_id]:
        raise HTTPException(status_code=400, detail="Target user is not part of this order")
    existing_review = db.query(Review).filter(
        Review.author_id == current_user.id,
        Review.target_id == review.target_id,
        Review.created_at >= db_order.created_at
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this user for an order")
    db_review = Review(
        author_id=current_user.id,
        target_id=review.target_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    recalculate_user_rating(review.target_id, db)
    return db_review