"""
Arbiter AI — WebSocket Manager
Manages real-time connection routing to feed events to the Observatory page.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections per session ID."""
    
    def __init__(self):
        # Maps session_id -> list of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Maps session_id -> list of event logs for replaying to late joiners
        self.event_cache: Dict[str, List[dict]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        
        # Replay any cached events so the client has full stream history
        if session_id in self.event_cache:
            for event in self.event_cache[session_id]:
                await websocket.send_json(event)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, session_id: str, message: dict):
        """Send message to all clients listening to a specific session_id."""
        # Cache the event first
        if session_id not in self.event_cache:
            self.event_cache[session_id] = []
        self.event_cache[session_id].append(message)
        
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Failed to send WS message: {e}")


manager = ConnectionManager()

@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket route to connect to the session observatory feed."""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Maintain connection, handle any client heartbeat or settings message
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Client might ask to ping or get status
                if msg.get("type") == "ping":
                    await websocket.send_json({"event": "pong"})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)
