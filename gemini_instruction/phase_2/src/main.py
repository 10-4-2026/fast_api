'''
Bước 5: Đăng ký Worker và Router vào vòng đời ứng dụng (main.py)
Cập nhật file khởi chạy chính để kích hoạt frame_consumer khi ứng dụng
 khởi động và gắn router WebSocket vào FastAPI app.
'''

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.adapters.database import engine, Base
from src.services.frame_consumer import frame_consumer
from src.services.telemetry_worker import telemetry_processor
from src.entrypoints.api import router as ws_router

# from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        pass

    # Khởi động các Background Workers (Telemetry + Frame Stream)
    await telemetry_processor.start()
    await frame_consumer.start()
    
    yield

    # Dừng Workers an toàn
    await telemetry_processor.stop()
    await frame_consumer.stop()
    await engine.dispose()
    pass

app = FastAPI(title="IoT Connected Vehicle Platform - Stream Engine", lifespan=lifespan)


# Gắn WebSocket Router
app.include_router(ws_router)