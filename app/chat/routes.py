from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user_ws, get_current_user
from ..auth.models import User
from ..chat.models import ChatMessage
from typing import Dict
from .schemas import ChatMessageResponse
from sqlalchemy import or_
from typing import List, Dict

router = APIRouter()

active_connections: Dict[int, WebSocket] = {}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user_ws)):
    await websocket.accept()
    active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            task_id = data.get("task_id")
            message = data.get("message")
            to_user_id = data.get("to")

            if not message or not to_user_id:
                await websocket.send_json({"error": "Message and to_user_id are required"})
                continue

            if current_user.id != user_id:
                await websocket.send_json({"error": "Unauthorized"})
                continue

            new_message = ChatMessage(
                sender_id=current_user.id,
                receiver_id=to_user_id,
                task_id=task_id,
                message=message
            )
            db.add(new_message)
            db.commit()

            if to_user_id in active_connections:
                await active_connections[to_user_id].send_json({
                    "sender_id": current_user.id,
                    "message": message,
                    "created_at": new_message.created_at.isoformat(),
                    "task_id": task_id
                })

    except WebSocketDisconnect:
        active_connections.pop(user_id, None)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        active_connections.pop(user_id, None)


@router.get("/messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
        with_user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    messages = db.query(ChatMessage).filter(
        or_(
            (ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == with_user_id),
            (ChatMessage.sender_id == with_user_id) & (ChatMessage.receiver_id == current_user.id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()

    return messages