'''
Bước 2: Xây dựng AsyncIO Producer-Consumer (Xử lý Telemetry thời gian thực)
Tại tầng src/services/telemetry_worker.py, ta xây dựng một hàng đợi bất đồng bộ (asyncio.Queue) để nhận dữ liệu từ các thiết bị Edge đẩy lên mà không làm nghẽn luồng xử lý chính của server.
'''

import asyncio
import logging

logger = logging.getLogger(__name__)

class TelemetryProcessor:
    def __init__(self):
        self.queue : asyncio.Queue() = asyncio.Queue(maxsize=1000)
        self._is_running = False
        self._worker_task = None

    async def _consume(self):
        """Consumer: Lấy dữ liệu từ hàng đợi ra xử lý bất đồng bộ"""
        while self._is_running:
            try:
                # Đợi dữ liệu từ queue với timeout để có thể check _is_running
                data = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                # Giả lập xử lý dữ liệu Telemetry (lưu DB, tính toán rule,...)
                await asyncio.sleep(0.1)
                logger.info(f"Processed telemetry data: {data}")

                self.queue.task_done()
                pass
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing telemetry: {e}")
            pass # end while
        pass # end _consume

    async def start(self):
        '''
        khởi động worker ngầm chạy nền
        '''
        self._is_running = True 
        self._worker_task = asyncio.create_task(self._consume())
        logger.info("Telemetry background worker started.")

        pass

    async def stop(self):
        """Dừng worker an toàn"""
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                logger.info("Telemetry background worker stopped.")
            pass
        pass
    
    async def push(self, data: dict):
        """Producer: Đẩy dữ liệu vào hàng đợi"""
        await self.queue.put(data)
        pass

    pass

# Khởi tạo một singleton instance dùng chung toàn ứng dụng
telemetry_processor = TelemetryProcessor()

    
    