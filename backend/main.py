from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.database import init_db
from app.api import players, leagues, drafts
from app.websocket import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FantasyDuel API",
    description="Fantasy football with unique 1v1 draft mechanics",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(leagues.router, prefix="/api/leagues", tags=["leagues"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["drafts"])


@app.get("/")
async def root():
    return {"message": "FantasyDuel API", "status": "active"}


@app.websocket("/ws/{draft_id}")
async def websocket_endpoint(websocket: WebSocket, draft_id: str):
    await manager.connect(websocket, draft_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(draft_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, draft_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
