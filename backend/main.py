from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.project import router as project_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    from db.init_db import init_db

    init_db()
    print("Database tables initialized")

    yield  # Return control

    # Shutdown: Any cleanup code would go here
    print("Application shutting down")


app = FastAPI()
app.include_router(chat_router)
app.include_router(project_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
