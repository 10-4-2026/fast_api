from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Lưu trữ danh sách kết nối active theo device_id
        self.active_connections: Dict[str, WebSocket] = {}
        pass
    
    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"Device {device_id} connected.")
        pass

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"Device {device_id} disconnected.")
        pass
 
    async def send_personal_message(self, message: dict, device_id: str):
        if device_id in self.active_connections:
            websocket = self.active_connections[device_id]
            await websocket.send_json(message)
            pass
        pass

manager = ConnectionManager()