import os
import sys
from contextlib import asynccontextmanager

# Under gunicorn stdout isn't a terminal, so Python block-buffers print()
# output and it can sit unflushed indefinitely - none of the scheduler's
# "[Reminder] ..." lines ever reached the Azure log stream. Line-buffering
# flushes each line as it's printed.
sys.stdout.reconfigure(line_buffering=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creates tables for any models that don't exist yet. It will NOT add columns
# to existing tables — use a migration (see migrate_add_grade_teacher.py) for that.
Base.metadata.create_all(bind=engine)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(api_router)
