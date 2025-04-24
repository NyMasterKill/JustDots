from fastapi import APIRouter, WebSocket, Depends, HTTPException
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.orders.models import Order, OrderStatus
from src.websocket.models import Message
from src.websocket.manager import chat_manager, notification_manager
from sqlalchemy.orm import Session
from src.database import get_db
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/chat/{order_id}")
async def chat_endpoint(
    websocket: WebSocket,
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        await websocket.close(code=1008, reason="Order not found")
        return
    is_customer = (db_order.customer_id == current_user.id)
    is_executor = (db_order.executor_id == current_user.id)
    if not (is_customer or is_executor):
        await websocket.close(code=1008, reason="Not authorized to chat for this order")
        return
    await chat_manager.connect(order_id, current_user.id, websocket)
    try:
        messages = db.query(Message).filter(Message.order_id == order_id).all()
        for msg in messages:
            await websocket.send_text(json.dumps({
                "user_id": msg.sender_id,
                "message": msg.content,
                "order_id": order_id,
                "created_at": msg.created_at.isoformat()
            }))
        while True:
            data = await websocket.receive_text()
            message = {
                "user_id": current_user.id,
                "message": data,
                "order_id": order_id,
                "created_at": datetime.utcnow().isoformat()
            }
            db_message = Message(
                order_id=order_id,
                sender_id=current_user.id,
                content=data
            )
            db.add(db_message)
            db.commit()
            await chat_manager.broadcast(order_id, message)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        chat_manager.disconnect(order_id, current_user.id, websocket)
        await websocket.close()

@router.websocket("/notifications/{user_id}")
async def notifications_endpoint(
    websocket: WebSocket,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        await websocket.close(code=1008, reason="Not authorized to receive notifications")
        return
    await notification_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        notification_manager.disconnect(user_id, websocket)
        await websocket.close()