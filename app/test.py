import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/chat/ws/2"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyb2xlcmthc3RlckBleGFtcGxlLmNvbSIsImV4cCI6MTc0NzI0OTI5NiwidHlwZSI6ImFjY2VzcyJ9.0Pl_5XGk-QNEyvRZpmx4iVSXeVIX4xfk0fpX0ZWFkkk"  # Замени на реальный токен
    }
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        message = {
            "task_id": 1,
            "message": "Привет, это тестовое сообщение!",
            "to": 3
        }
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Получено: {response}")

asyncio.run(test_websocket())