from fastapi import FastAPI
from single_model.api.users import router as users_router

app = FastAPI(title="FastAPI app")

app.include_router(users_router)

