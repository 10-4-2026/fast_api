'''
Bước 4: Định nghĩa ORM Model (Tầng Adapter)
'''
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from phase_1.adapters.database import Base


class DeviceTelemetryModel(Base):
    __tablename__ = "device_telemetries"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
        )
    device_id: Mapped[str] = mapped_column(index=True)
    speed: Mapped[float] = mapped_column()
    battery_level: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


