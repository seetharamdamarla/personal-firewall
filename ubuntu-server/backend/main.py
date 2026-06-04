from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import aiofiles
import os

from app.database import engine, Base
from app.routers import firewall

# Create SQLite Database Tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Firewall SOC API",
    description="Backend for managing nftables and streaming Suricata/Wazuh alerts",
    version="1.0.0"
)

# CORS is required so our React frontend can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(firewall.router)

# WebSocket connection manager for live alert streaming
active_connections = []

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Wait for client to send ping, or we can broadcast independently
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# A helper we can use later to broadcast Suricata/Wazuh alerts to the React UI
async def broadcast_alert(alert_data: dict):
    dead_connections = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(alert_data))
        except Exception:
            dead_connections.append(connection)
    for dead in dead_connections:
        if dead in active_connections:
            active_connections.remove(dead)

async def tail_log_file():
    log_path = "/var/log/personal-firewall/blocks.jsonl"
    
    # Create file if it doesn't exist to prevent errors
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, 'a') as f:
            pass
            
    async with aiofiles.open(log_path, mode='r') as f:
        # Seek to the end of the file so we only get new alerts
        await f.seek(0, 2)
        while True:
            line = await f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
            try:
                alert_data = json.loads(line)
                await broadcast_alert(alert_data)
            except json.JSONDecodeError:
                pass

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(tail_log_file())

@app.get("/")
def read_root():
    return {"status": "online", "message": "Personal Firewall SOC API is running"}
