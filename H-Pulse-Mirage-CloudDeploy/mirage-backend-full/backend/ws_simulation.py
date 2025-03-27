from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
from datetime import datetime

router = APIRouter()
clients: List[WebSocket] = []
simulation_state = {
    "status": "idle",  # idle / running / paused
    "tick": 0,
    "last_update": str(datetime.utcnow())
}

@router.websocket("/ws/simulation")
async def simulation_websocket(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        await send_state(websocket)
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "command":
                await handle_command(message["command"], websocket)
            elif message["type"] == "heartbeat":
                await websocket.send_text(json.dumps({"type": "heartbeat_ack"}))

    except WebSocketDisconnect:
        clients.remove(websocket)

async def handle_command(command: str, websocket: WebSocket):
    global simulation_state
    if command == "start":
        simulation_state["status"] = "running"
    elif command == "pause":
        simulation_state["status"] = "paused"
    elif command == "resume":
        simulation_state["status"] = "running"
    elif command == "reset":
        simulation_state["status"] = "idle"
        simulation_state["tick"] = 0
    elif command == "tick":
        simulation_state["tick"] += 1

    simulation_state["last_update"] = str(datetime.utcnow())
    await broadcast_state()

async def send_state(websocket: WebSocket):
    await websocket.send_text(json.dumps({
        "type": "state",
        "payload": simulation_state
    }))

async def broadcast_state():
    message = json.dumps({
        "type": "state",
        "payload": simulation_state
    })
    for client in clients:
        await client.send_text(message)
