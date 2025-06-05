from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, draft_id: str):
        await websocket.accept()
        if draft_id not in self.active_connections:
            self.active_connections[draft_id] = []
        self.active_connections[draft_id].append(websocket)

    def disconnect(self, websocket: WebSocket, draft_id: str):
        if draft_id in self.active_connections:
            self.active_connections[draft_id].remove(websocket)
            if not self.active_connections[draft_id]:
                del self.active_connections[draft_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, draft_id: str, message: str):
        if draft_id in self.active_connections:
            for connection in self.active_connections[draft_id]:
                await connection.send_text(message)


manager = ConnectionManager()
