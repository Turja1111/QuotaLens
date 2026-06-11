"""WebSocket live quota stream — pushes updates every 10 seconds."""

import json
import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from database import async_session
from crud import quota as quota_crud

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


@router.websocket("/ws/quota")
async def quota_websocket(websocket: WebSocket):
    """
    Live WebSocket stream — quota updates pushed every 10 seconds.
    Sends all current quota snapshots to connected clients.
    """
    await manager.connect(websocket)
    try:
        while True:
            try:
                async with async_session() as session:
                    snapshots = await quota_crud.get_latest_snapshots(session)
                payload = json.dumps(
                    [s.to_dict() for s in snapshots],
                    default=str,
                )
                await websocket.send_text(payload)
            except Exception as e:
                logger.error(f"Error fetching quota for WebSocket: {e}")
                await websocket.send_text(json.dumps({"error": str(e)}))

            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
