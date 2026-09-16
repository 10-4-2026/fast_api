from fastapi import FastAPI
from app.presentation.api.routers.user_router import router

app = FastAPI()

app.include_router(router)

@app.get("/")
async def health():
    return {
        "status": "ok"
    }