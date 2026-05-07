from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

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
    for connection in active_connections:
        await connection.send_text(json.dumps(alert_data))

@app.get("/")
def read_root():
    return {"status": "online", "message": "Personal Firewall SOC API is running"}
