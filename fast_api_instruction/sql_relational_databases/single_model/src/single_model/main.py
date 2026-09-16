from typing import Annotated # Dùng để gắn metadata cho kiểu dữ liệu.

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


'''
Tại sao kế thừa SQLModel ?

Vì SQLModel cung cấp:
    ORM mapping
    Data validation (Pydantic)
    Serialization JSON

table=True
    Python
    table=True

    Có nghĩa:
    Python
    Hero <-> Table Hero trong database
    
    Nếu bỏ:

    Python    
    table=False
    
    Thì chỉ là model dữ liệu, không tạo bảng.
    '''
class Hero(SQLModel, table=True):
    '''
    Vì sao default=None ?

        Khi insert:

        Python
        {
        "name": "Batman"
        }
        Client không cần gửi id.
        Database tự sinh.
    '''
    id : int | None = Field(default=None, primary_key=True)
    name : str = Field(index=True)
    '''
    Nếu không index:
            Full Table Scan

    Nếu có index:
            B-Tree Search

        Nhanh hơn nhiều.
    '''
    age : int | None = Field(default=None, index=True)
    secret_name: str # Bắt buộc nhập.
    pass 

sqlite_file_name = "database.db"
'''
Tại sao 3 dấu /
    sqlite:///
    Là cú pháp chuẩn SQLite local file.
'''
sqlite_url = f"sqlite:///{sqlite_file_name}"


'''
5. connect_args
    connect_args = {"check_same_thread": False}
    SQLite mặc định:
     connection
chỉ dùng trong 1 thread

Trong FastAPI:

Request A -> Thread A
Request B -> Thread B

Có thể bị lỗi:

SQLite objects created in a thread can only be used in that same thread
Vì vậy cần:

check_same_thread=False
để cho phép nhiều thread sử dụng.
'''
connect_args = {
    "check_same_thread": False
}
engine  = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
        pass
    pass

# session có kiểu Session
# và được inject bởi Depends(get_session)
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

'''
Startup
    ↓
on_startup()
    ↓
create_db_and_tables()
'''
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    pass

@app.post("/heroes/")
def create_hero(hero: Hero, 
                session : SessionDep
                ) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/herors/")
def read_heroes(
    session : SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset=offset).limit(limit=limit)).all()
    return heroes

@app.get("/herors/{hero_id}")
def read_heroe(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.delete("/herors/{hero_id}")
def read_heroe(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


'''
Dependency Injection (DI) là một trong những khái niệm quan trọng nhất của FastAPI. Nếu chỉ nhìn code:

session: SessionDep


thì có vẻ FastAPI "tự nhiên" tạo ra session cho chúng ta. Thực tế đằng sau là cả một cơ chế quản lý dependency rất mạnh.

1. Vấn đề DI sinh ra để giải quyết là gì?

Giả sử không dùng DI:

@app.get("/heroes/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


Nhược điểm:

API nào cũng phải tự mở session
API nào cũng phải tự đóng session
Lặp code
Khó test
Khó thay thế database

Ví dụ có 100 API:

@app.get(...)
@app.post(...)
@app.delete(...)
...


thì sẽ phải lặp lại:

with Session(engine) as session:


100 lần.

2. Ý tưởng của DI

Thay vì API tự tạo Session:

session = Session(engine)


ta nói với FastAPI:

"Muốn có Session thì hãy dùng hàm get_session()"

def get_session():
    with Session(engine) as session:
        yield session


Sau đó:

session: Session = Depends(get_session)


FastAPI sẽ:

API cần Session
      ↓
FastAPI gọi get_session()
      ↓
Tạo Session
      ↓
Truyền Session vào API
      ↓
API chạy
      ↓
Đóng Session

3. Dependency là gì?

Một dependency đơn giản:

def get_name():
    return "Long"


API:

@app.get("/")
def home(name=Depends(get_name)):
    return {"name": name}


Request:

GET /


FastAPI thực hiện:

name = get_name()

home(name)


Thực tế tương đương:

home("Long")


Kết quả:

{
  "name": "Long"
}

4. Session Dependency hoạt động thế nào?

Trong code của bạn:

def get_session():
    with Session(engine) as session:
        yield session


Giả sử request:

GET /heroes


Endpoint:

def read_heroes(session: SessionDep):


FastAPI nhìn thấy:

SessionDep


mà SessionDep được khai báo:

SessionDep = Annotated[
    Session,
    Depends(get_session)
]


FastAPI hiểu rằng:

Muốn có session
→ gọi get_session()

5. Tại sao dùng yield thay vì return?

Nhiều người thắc mắc:

def get_session():
    return Session(engine)


có được không?

Được, nhưng không tốt.

Với:

yield


FastAPI quản lý vòng đời dependency.

Ví dụ:

def get_session():
    print("OPEN")

    with Session(engine) as session:
        yield session

    print("CLOSE")


Request:

GET /heroes


Log:

OPEN

(API chạy)

CLOSE


Điều này giống:

try:
    session = Session(engine)

    # API xử lý

finally:
    session.close()


FastAPI tự làm giúp.

6. Luồng thực tế của FastAPI

Khi gọi:

GET /heroes


FastAPI làm 7 bước:

B1: Nhận request
GET /heroes

B2: Phân tích endpoint
def read_heroes(session: SessionDep)


Phát hiện:

Depends(get_session)

B3: Gọi dependency
get_session()

B4: Tạo session
Session(engine)

B5: Inject

Tương đương:

read_heroes(
    session=session_object
)

B6: API chạy
heroes = session.exec(...)

B7: Cleanup

Sau khi API xong:

session.close()


Luồng:

Request
   ↓
Depends(get_session)
   ↓
Create Session
   ↓
Inject Session
   ↓
Run API
   ↓
Close Session
   ↓
Response

7. Tại sao gọi là "Injection"?

Từ "Inject" nghĩa là "bơm vào".

Ví dụ:

def hello(name):
    print(name)


Bạn gọi:

hello("Long")


thì:

"Long"


được inject vào parameter name.

Trong FastAPI:

def read_heroes(session: SessionDep):


FastAPI tự inject:

Session(...)


vào biến:

session

8. Dependency lồng nhau

FastAPI hỗ trợ Dependency Chain.

Ví dụ:

def get_db():
    yield Session(engine)

def get_repo(
    db = Depends(get_db)
):
    return HeroRepository(db)

@app.get("/heroes")
def get_heroes(
    repo = Depends(get_repo)
):
    return repo.get_all()


Luồng:

Endpoint
   ↓
get_repo
   ↓
get_db
   ↓
Session


FastAPI tự resolve toàn bộ.

9. Lợi ích lớn nhất khi Test

Không DI:

Session(engine)


bị hard-code.

Test rất khó.

Có DI:

Depends(get_session)


Test có thể override:

def fake_session():
    yield test_session

app.dependency_overrides[
    get_session
] = fake_session


Lúc này API dùng:

test database


thay vì:

production database


Đây là lý do các framework hiện đại rất chuộng DI.

10. Tại sao dùng Annotated?

Cũ:

def create_hero(
    session: Session = Depends(get_session)
):


Mỗi endpoint phải viết lại.

FastAPI mới khuyến khích:

SessionDep = Annotated[
    Session,
    Depends(get_session)
]


Sau đó:

def create_hero(
    session: SessionDep
):


Ngắn gọn hơn.

11. Minh họa bằng đời thường

Hãy tưởng tượng:

Restaurant API


Muốn nấu ăn cần:

Bếp
Dao
Gas


Nếu mỗi đầu bếp tự đi lấy:

Dao
Gas
Bếp


thì rất rối.

Dependency Injection:

Nhà hàng chuẩn bị sẵn
      ↓
Đầu bếp chỉ việc nhận
      ↓
Nấu ăn
      ↓
Trả lại dụng cụ


Trong FastAPI:

Dao/Gas/Bếp
   ↓
Session

Đầu bếp
   ↓
Endpoint Function

Nhà hàng cung cấp
   ↓
Depends(...)

Tóm tắt ngắn gọn

Đối với đoạn code của bạn:

SessionDep = Annotated[
    Session,
    Depends(get_session)
]


và

def get_session():
    with Session(engine) as session:
        yield session


thì mỗi request sẽ diễn ra như sau:

Request tới API
        ↓
FastAPI phát hiện cần Session
        ↓
Gọi get_session()
        ↓
Tạo Session(engine)
        ↓
Inject Session vào hàm API
        ↓
API thao tác DB
        ↓
Session tự đóng sau khi hoàn tất


Nói ngắn gọn: Dependency Injection là cơ chế để FastAPI tự động tạo, quản lý vòng đời và truyền các đối tượng cần thiết (Session, User, Config, Service, Repository...) vào endpoint thay vì endpoint phải tự khởi tạo chúng.
'''


