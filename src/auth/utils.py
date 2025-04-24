from sqlalchemy.orm import Session
from src.auth.models import User
from src.reviews.models import Review

def recalculate_user_rating(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    reviews = db.query(Review).filter(Review.target_id == user_id).all()
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
        user.rating = avg_rating
        db.commit()