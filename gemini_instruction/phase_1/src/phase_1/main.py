'''
Bước 5: Xây dựng FastAPI Entrypoint & Quản lý Lifespan
Tại src/main.py, kết nối toàn bộ hệ thống bằng cơ chế Lifespan của 
FastAPI (khởi động background worker khi app chạy và tắt an toàn khi app dừng).
'''

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from phase_1.adapters.database import get_db_session, engine, Base
from phase_1.adapters.orm_models import DeviceTelemetryModel
from phase_1.services.telemetry_worker import telemetry_processor

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Khởi tạo database tables (hoặc dùng Alembic migration)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        pass
    # 2. Khởi chạy background worker
    await telemetry_processor.start()

    yield

    # Stop background worker
    # 3. Dọn dẹp tài nguyên khi tắt ứng dụng
    await telemetry_processor.stop()
    await engine.dispose()
    pass

app = FastAPI(
    title="IoT Connected Vehicle Platform",
    version="1.0.0",
    lifespan=lifespan
    )

@app.post("/api/v1/telemetry")
async def receive_telemetry(data: dict):
    """API nhận dữ liệu từ Edge Device và đẩy vào Async Queue"""
    # Đẩy dữ liệu vào hàng đợi bất đồng bộ ngay lập tức để trả về response nhanh
    await telemetry_processor.push(data)
    return {
        "status": "accepted", "message": "Telemetry queued for processing"
    }

@app.get("/api/v1/devices/{device_id}/logs")
async def get_device_logs(device_id: str, db: AsyncSession = Depends(get_db_session)):
    """API lấy dữ liệu Telemetry từ DB cho thiết bị cụ thể"""
    from sqlalchemy import select
    result = await db.execute(
        select(DeviceTelemetryModel).where(DeviceTelemetryModel.device_id == device_id)
    )
    logs = result.scalars().all()
    return {
        "device_id": device_id, "data": logs
    }
