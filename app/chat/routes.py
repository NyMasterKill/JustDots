from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user_ws
from ..auth.models import User
from ..chat.models import ChatMessage
from typing import Dict

router = APIRouter()

# Хранилище активных подключений (user_id -> WebSocket)
active_connections: Dict[int, WebSocket] = {}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_ws)):
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

            # Проверка, что текущий пользователь — отправитель
            if current_user.id != user_id:
                await websocket.send_json({"error": "Unauthorized"})
                continue

            # Создание и сохранение сообщения в БД
            new_message = ChatMessage(
                sender_id=current_user.id,
                receiver_id=to_user_id,
                task_id=task_id,
                message=message
            )
            db.add(new_message)
            db.commit()

            # Отправка сообщения получателю, если он онлайн
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