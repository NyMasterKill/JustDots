from fastapi import WebSocket
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[tuple[int, WebSocket]]] = {}

    async def connect(self, order_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append((user_id, websocket))

    def disconnect(self, order_id: int, user_id: int, websocket: WebSocket):
        if order_id in self.active_connections:
            self.active_connections[order_id] = [
                (uid, ws) for uid, ws in self.active_connections[order_id]
                if ws != websocket
            ]
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def broadcast(self, order_id: int, message: dict):
        if order_id in self.active_connections:
            for user_id, websocket in self.active_connections[order_id]:
                await websocket.send_text(json.dumps(message))

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id]
                if ws != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_notification(self, user_id: int, notification: dict):
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                await websocket.send_text(json.dumps(notification))

chat_manager = ConnectionManager()
notification_manager = NotificationManager()