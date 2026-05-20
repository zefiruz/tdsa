from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import os
from app.routers import tasks, users, admin

app = FastAPI(title="Task Manager API")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "env": os.getenv("APP_ENV", "local")}

class RoomManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][username] = websocket
        await self.broadcast(room_id, {"type": "join", "username": username})

    def disconnect(self, room_id: str, username: str):
        if room_id in self.rooms and username in self.rooms[room_id]:
            del self.rooms[room_id][username]
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self.rooms:
            for ws in self.rooms[room_id].values():
                await ws.send_json(payload)

    def get_users(self, room_id: str):
        return list(self.rooms.get(room_id, {}).keys())

manager = RoomManager()

@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = Query(default="")):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, username, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                text = data.get("text", "")
                if len(text) > 300:
                    await websocket.send_json({"type": "error", "detail": "Message is too long"})
                else:
                    await manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    except WebSocketDisconnect:
        manager.disconnect(room_id, username)

@app.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    return {"room_id": room_id, "users": manager.get_users(room_id)}