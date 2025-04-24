from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.database import get_db
from src.orders.models import Order, OrderStatus
from src.orders.schemas import OrderCreate, Order
from src.categories.models import Category
from src.order_responses.models import OrderResponse, ResponseStatus
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.websocket.manager import notification_manager

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=Order)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Only clients can create orders")
    db_category = db.query(Category).filter(Category.id == order.category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_order = Order(
        title=order.title,
        description=order.description,
        budget_from=order.budget_from,
        budget_to=order.budget_to,
        deadline=order.deadline,
        category_id=order.category_id,
        skills_text=order.skills_text,
        requirements=order.requirements,
        customer_id=current_user.id,
        status=OrderStatus.OPEN
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=list[Order])
def get_orders(
    category_id: Optional[int] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    status: Optional[str] = "open",
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if category_id:
        query = query.filter(Order.category_id == category_id)
    if min_budget:
        query = query.filter(Order.budget_from >= min_budget)
    if max_budget:
        query = query.filter(Order.budget_to <= max_budget)
    return query.all()

@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this order")
    if db_order.status == OrderStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot edit a closed order")
    db_order.title = order.title
    db_order.description = order.description
    db_order.budget_from = order.budget_from
    db_order.budget_to = order.budget_to
    db_order.deadline = order.deadline
    db_order.category_id = order.category_id
    db_order.skills_text = order.skills_text
    db_order.requirements = order.requirements
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/{order_id}/close", response_model=Order)
def close_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to close this order")
    if db_order.status != OrderStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Order must be in progress to close")
    db_order.status = OrderStatus.CLOSED
    db.commit()
    db.refresh(db_order)
    return db_order

@router.post("/{order_id}/select/{response_id}", response_model=Order)
async def select_executor(
    order_id: int,
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if db_order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to select executor")
    if db_order.status != OrderStatus.OPEN:
        raise HTTPException(status_code=400, detail="Order must be open to select executor")
    db_response = db.query(OrderResponse).filter(OrderResponse.id == response_id).first()
    if not db_response or db_response.order_id != order_id:
        raise HTTPException(status_code=404, detail="Response not found or does not belong to this order")
    db_order.executor_id = db_response.user_id
    db_order.status = OrderStatus.IN_PROGRESS
    db_response.status = ResponseStatus.ACCEPTED
    other_responses = db.query(OrderResponse).filter(
        and_(OrderResponse.order_id == order_id, OrderResponse.id != response_id)
    ).all()
    for r in other_responses:
        r.status = ResponseStatus.REJECTED
    db.commit()
    db.refresh(db_order)
    notification = {
        "type": "executor_selected",
        "order_id": order_id,
        "message": f"You have been selected as the executor for order {order_id}"
    }
    await notification_manager.send_notification(db_response.user_id, notification)
    return db_order