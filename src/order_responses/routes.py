from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.order_responses.models import OrderResponse, ResponseStatus
from src.order_responses.schemas import OrderResponseCreate, OrderResponse
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.orders.models import Order, OrderStatus

router = APIRouter(prefix="/order_responses", tags=["order_responses"])

@router.post("/", response_model=OrderResponse)
def create_order_response(
    response: OrderResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Only freelancers can respond to orders")
    db_order = db.query(Order).filter(
        Order.id == response.order_id,
        Order.status == OrderStatus.OPEN
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found or not open")
    existing_response = db.query(OrderResponse).filter(
        OrderResponse.order_id == response.order_id,
        OrderResponse.user_id == current_user.id
    ).first()
    if existing_response:
        raise HTTPException(status_code=400, detail="You have already responded to this order")
    db_response = OrderResponse(
        order_id=response.order_id,
        user_id=current_user.id,
        proposed_price=response.proposed_price,
        comment=response.comment,
        status=ResponseStatus.PENDING
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response