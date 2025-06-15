import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncpg

router = APIRouter()
clients = set()

async def listen_to_db():
    conn = await asyncpg.connect(dsn="postgresql://postgres:postgres@localhost:5432/rainman")
    await conn.add_listener("trade_updates", db_notify_handler)
    while True:
        await asyncio.sleep(60)

async def db_notify_handler(connection, pid, channel, payload):
    for ws in clients.copy():
        try:
            await ws.send_text(payload)
        except:
            clients.remove(ws)

@router.websocket("/ws/trades")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # optional: keepalive or ping
    except WebSocketDisconnect:
        clients.remove(websocket)
