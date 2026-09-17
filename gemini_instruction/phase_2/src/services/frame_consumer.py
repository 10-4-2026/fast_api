'''
Bước 3: Xây dựng Stream Data Consumer (Xử lý khung hình/Telemetry tần suất cao)
Tại src/services/frame_consumer.py, xây dựng hàng đợi chuyên biệt để xử lý dữ liệu nặng 
(như luồng video hoặc stream cảm biến từ xe) một cách tuần tự hoặc song song an toàn.
'''

import asyncio
import logging

logger = logging.getLogger(__name__)

class FrameStreamConsumer:
    def __init__(self):
        # Hàng đợi chứa các khung hình hoặc gói tin dữ liệu lớn
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=100)  # Giới hạn số lượng khung hình trong hàng đợi
        self._is_running = False
        self._worker_task = None

    async def start(self):
        self._is_running = True
        # Có thể khởi chạy nhiều worker song song nếu hệ thống lớn (ví dụ: tạo 2-3 task)
        self._worker_task = asyncio.create_task(self._consume_loop())
        logger.info("Frame Stream Consumer worker started.")
        pass

    async def stop(self):
        self._is_running = False
        if self._worker_task:
            #await self._worker_task.cancel()
            # Bỏ 'await' ở phương thức cancel()
            self._worker_task.cancel()
            try:
                await self._worker_task
                pass
            except asyncio.CancelledError:
                logger.info("Frame Stream Consumer worker stopped.")
                pass
            pass        
        pass
    
    async def push_frame(self, device_id: str, frame_data: bytes):
        """Đẩy dữ liệu khung hình vào queue từ WebSocket endpoint"""
        if self.queue.full():
            logger.warning("Frame queue is full! Dropping frame to prevent memory overflow.")
            return
        await self.queue.put({"device_id": device_id, "data": frame_data})

    async def _consume_loop(self):
        while self._is_running:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)  # Chờ item trong 1 giây
                #device_id, frame_data = item
                device_id = item["device_id"]
                frame_data = item["data"]

                # Giả lập xử lý Computer Vision / AI Inference trên Frame
                await asyncio.sleep(0.05) 
                logger.info(f"Processed frame from {device_id} | Size: {len(frame_data)} bytes")

                self.queue.task_done()
                pass
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing frame stream: {e}")
            pass
        pass
    pass

frame_consumer = FrameStreamConsumer()