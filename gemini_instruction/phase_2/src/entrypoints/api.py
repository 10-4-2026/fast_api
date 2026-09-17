# src/entrypoints/api.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging


'''
# Cấu hình lưu log ra file app.log
logging.basicConfig(
    filename="api.log",  # File log sẽ xuất hiện cùng thư mục chạy lệnh
    filemode="a",        # "a" = ghi tiếp vào cuối file (append)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

'''
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws/v1", tags=["IoT WebSocket Stream"])

@router.websocket("/vehicle/{device_id}")
async def vehicle_stream_endpoint(websocket: WebSocket, device_id: str):
    # Chấp nhận kết nối ngay lập tức trước khi đọc dữ liệu
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_bytes()
            # Xử lý dữ liệu...
            await websocket.send_json({"status": "received something", "bytes": len(data)})
    except WebSocketDisconnect:
        print(f"Device disconnected: {device_id}")