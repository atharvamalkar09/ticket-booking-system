import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.routes import (
    adminDashboard,
    auth,
    bookings,
    events,
    payment,
    seats,
    users,
    venues,
)
from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import BaseAppException
from app.db.database import get_db
from app.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.tasks.booking_expiry import booking_expiry_worker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(
        booking_expiry_worker()
    )

    try:
        yield
    finally:
        worker_task.cancel()

        try:
            await worker_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Ticket Booking System API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_exception_handler(
    BaseAppException,
    app_exception_handler
)


origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


app.include_router(
    auth.router,
    prefix="/api/v1"
)

app.include_router(
    users.router,
    prefix="/api/v1"
)

app.include_router(
    venues.router,
    prefix="/api/v1"
)

app.include_router(
    events.router,
    prefix="/api/v1"
)

app.include_router(
    bookings.router,
    prefix="/api/v1"
)

app.include_router(
    seats.router,
    prefix="/api/v1"
)

app.include_router(
    adminDashboard.router,
    prefix="/api/v1"
)

app.include_router(
    payment.router,
    prefix="/api/v1"
)


@app.get("/db")
def check(db: Session = Depends(get_db)):
    return {
        "message": "Connection Successful"
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "ok"
    }