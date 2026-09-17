Dưới đây là hướng dẫn từng bước viết code cho **Giai đoạn 2: IoT Communication & Stream Processing**, tập trung xây dựng hệ thống giao tiếp thời gian thực qua **WebSocket** và xử lý luồng dữ liệu lớn (như khung hình video, cảm biến tốc độ cao) bằng mô hình **Producer-Consumer kết hợp Queue bất đồng bộ**.

---

### **Bước 1: Mở rộng cấu trúc thư mục cho Real-time Stream**

Cập nhật thêm các module xử lý WebSocket và Stream Consumer vào cấu trúc dự án:

```text
my_iot_platform/
│
├── src/
│   ├── adapters/
│   │   ├── database.py
│   │   ├── orm_models.py
│   │   └── websocket_manager.py     # Quản lý kết nối WebSocket từ Edge/Vehicle
│   ├── services/
│   │   ├── telemetry_worker.py
│   │   └── frame_consumer.py        # Xử lý luồng dữ liệu lớn (Frame/Stream)
│   ├── entrypoints/
│   │   └── api.py                   # Thêm WebSocket Router
│   └── main.py

```

---

### **Bước 2: Xây dựng WebSocket Connection Manager**

Tầng `src/adapters/websocket_manager.py` dùng để quản lý các kết nối đang mở từ các thiết bị xe thông minh (Edge Devices) đẩy lên server.

```python
# src/adapters/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Lưu trữ danh sách kết nối active theo device_id
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        logger.info(f"Device connected: {device_id}")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            logger.info(f"Device disconnected: {device_id}")

    async def send_personal_message(self, message: dict, device_id: str):
        if device_id in self.active_connections:
            websocket = self.active_connections[device_id]
            await websocket.send_json(message)

manager = ConnectionManager()

```

---

### **Bước 3: Xây dựng Stream Data Consumer (Xử lý khung hình/Telemetry tần suất cao)**

Tại `src/services/frame_consumer.py`, xây dựng hàng đợi chuyên biệt để xử lý dữ liệu nặng (như luồng video hoặc stream cảm biến từ xe) một cách tuần tự hoặc song song an toàn.

```python
# src/services/frame_consumer.py
import asyncio
import logging

logger = logging.getLogger(__name__)

class FrameStreamConsumer:
    def __init__(self):
        # Hàng đợi chứa các khung hình hoặc gói tin dữ liệu lớn
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        self._is_running = False
        self._worker_task = None

    async def start(self):
        self._is_running = True
        # Có thể khởi chạy nhiều worker song song nếu hệ thống lớn (ví dụ: tạo 2-3 task)
        self._worker_task = asyncio.create_task(self._consume_loop())
        logger.info("Frame Stream Consumer worker started.")

    async def stop(self):
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                logger.info("Frame Stream Consumer worker stopped.")

    async def push_frame(self, device_id: str, frame_data: bytes):
        """Đẩy dữ liệu khung hình vào queue từ WebSocket endpoint"""
        if self.queue.full():
            logger.warning("Frame queue is full! Dropping frame to prevent memory overflow.")
            return
        await self.queue.put({"device_id": device_id, "data": frame_data})

    async def _consume_loop(self):
        while self._is_running:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                device_id = item["device_id"]
                frame_data = item["data"]

                # Giả lập xử lý Computer Vision / AI Inference trên Frame
                await asyncio.sleep(0.05) 
                logger.info(f"Processed frame from {device_id} | Size: {len(frame_data)} bytes")

                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing frame stream: {e}")

frame_consumer = FrameStreamConsumer()

```

---

### **Bước 4: Tích hợp WebSocket Endpoint vào FastAPI Entrypoint**

Tại `src/entrypoints/api.py` (hoặc tích hợp trực tiếp vào `main.py`), tạo endpoint WebSocket để nhận dữ liệu nhị phân (binary stream) trực tiếp từ thiết bị Edge.

```python
# src/entrypoints/api.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.adapters.websocket_manager import manager
from src.services.frame_consumer import frame_consumer

router = APIRouter(prefix="/ws/v1", tags=["IoT WebSocket Stream"])

@router.websocket("/vehicle/{device_id}")
async def vehicle_stream_endpoint(websocket: WebSocket, device_id: str):
    """
    Endpoint WebSocket nhận luồng dữ liệu thời gian thực từ xe (ví dụ: hình ảnh camera, cảm biến liên tục)
    """
    await manager.connect(device_id, websocket)
    try:
        while True:
            # Nhận dữ liệu dạng bytes (khung hình camera hoặc packet thô) từ thiết bị
            data = await websocket.receive_bytes()
            
            # Đẩy vào background worker xử lý stream bất đồng bộ
            await frame_consumer.push_frame(device_id, data)
            
            # Gửi phản hồi (Acknowledgment / Lệnh điều khiển tức thời) về cho xe
            await websocket.send_json({"status": "received", "bytes": len(data)})
            
    except WebSocketDisconnect:
        manager.disconnect(device_id)
    except Exception as e:
        logger_err = str(e)
        print(f"WebSocket error for {device_id}: {logger_err}")
        manager.disconnect(device_id)

```

---

### **Bước 5: Đăng ký Worker và Router vào vòng đời ứng dụng (`main.py`)**

Cập nhật file khởi chạy chính để kích hoạt `frame_consumer` khi ứng dụng khởi động và gắn router WebSocket vào FastAPI app.

```python
# src/main.py (Cập nhật bổ sung Giai đoạn 2)
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.adapters.database import engine, Base
from src.services.telemetry_worker import telemetry_processor
from src.services.frame_consumer import frame_consumer
from src.entrypoints.api import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Khởi động các Background Workers (Telemetry + Frame Stream)
    await telemetry_processor.start()
    await frame_consumer.start()
    
    yield
    
    # Dừng Workers an toàn
    await telemetry_processor.stop()
    await frame_consumer.stop()
    await engine.dispose()

app = FastAPI(title="IoT Connected Vehicle Platform - Stream Engine", lifespan=lifespan)

# Gắn WebSocket Router
app.include_router(ws_router)

```

---

### **Bước 6: Kiểm thử luồng Stream WebSocket**

Bạn có thể viết một script Python nhỏ sử dụng thư viện `websockets` để giả lập một thiết bị Edge gửi dữ liệu liên tục lên server:

```python
import asyncio
import websockets

async def simulate_edge_device():
    uri = "ws://localhost:8000/ws/v1/vehicle/car_unit_01"
    async with websockets.connect(uri) as websocket:
        for i in range(10):
            # Giả lập gói tin khung hình nhị phân (binary data)
            fake_frame_bytes = b"\xFF\xD8\xFF\xE0" + b"\x00" * 1024 
            await websocket.send(fake_frame_bytes)
            
            response = await websocket.recv()
            print(f"Server response: {response}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(simulate_edge_device())

```

