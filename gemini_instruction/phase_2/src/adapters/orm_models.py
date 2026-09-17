'''
Bước 4: Định nghĩa ORM Model (Tầng Adapter)
'''
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
'''
mapped_column dùng để định nghĩa chi tiết của cột:
kiểu dữ liệu, primary key, index, default value, nullable, unique
'''
from adapters.database import Base


'''
Đây là một Model ORM của SQLAlchemy 2.0, dùng để ánh xạ (mapping) 
dữ liệu trong Python sang một bảng trong cơ sở dữ liệu.
'''
class DeviceTelemetryModel(Base):
    '''
    Nếu gọi: Base.metadata.create_all()
    sẽ sinh ra:
    CREATE TABLE device_telemetries (
    ...
    );
    '''
    __tablename__ = "device_telemetries"

    # tương đương id INTEGER PRIMARY KEY AUTOINCREMENT
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True
        )
    # Dùng để khai báo kiểu dữ liệu ORM theo chuẩn mới.
    # name là một cột database kiểu string
    # Định nghĩa mã thiết bị. 
    # == device_id VARCHAR
    # CREATE INDEX idx_device_id ON device_telemetries(device_id);
    device_id: Mapped[str] = mapped_column(index=True) 
    speed: Mapped[float] = mapped_column() # == speed FLOAT trong SQL
    battery_level: Mapped[float] = mapped_column()
    # default=datetime.utcnow == SQLAlchemy sẽ gọi: datetime.utcnow() mỗi lần insert.
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


