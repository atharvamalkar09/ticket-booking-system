import os
from uuid import uuid4

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from app.models.venue import Venue
from app.models.seat import Seat, SeatCategory
from app.models.event import Event

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db


DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("POSTGRES_HOST", "host.docker.internal")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")

TEST_DB_NAME = "ticketbooking_test"

TEST_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@localhost:{DB_PORT}/{TEST_DB_NAME}"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def booking_test_data():
    db = TestingSessionLocal()

    unique_id = uuid4().hex[:8]

    venue = Venue(
        name=f"Test Cinema {unique_id}",
        location="Kolhapur",
        capacity=10,
        description="Integration test venue"
    )

    db.add(venue)
    db.flush()

    seat_1 = Seat(
        venue_id=venue.id,
        row="A",
        number=1,
        category=SeatCategory.STANDARD
    )

    seat_2 = Seat(
        venue_id=venue.id,
        row="A",
        number=2,
        category=SeatCategory.STANDARD
    )

    db.add_all([seat_1, seat_2])
    db.flush()

    other_venue = Venue(
        name=f"Other Test Venue {unique_id}",
        location="Kolhapur",
        capacity=10,
        description="Venue not associated with this event"
    )

    db.add(other_venue)
    db.flush()

    other_seat = Seat(
        venue_id=other_venue.id,
        row="B",
        number=1,
        category=SeatCategory.STANDARD
    )

    db.add(other_seat)
    db.flush()

    now = datetime.now(timezone.utc)

    event = Event(
        title=f"Test Movie {unique_id}",
        description="Integration test event",
        category="MOVIE",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=2),
        base_price=Decimal("250.00"),
        venues=[venue]
    )

    db.add(event)
    db.commit()

    db.refresh(venue)
    db.refresh(seat_1)
    db.refresh(seat_2)
    db.refresh(event)

    yield {
        "venue": venue,
        "seat_1": seat_1,
        "seat_2": seat_2,
        "other_venue": other_venue,
        "other_seat": other_seat,
        "event": event,
    }

    db.close()


@pytest.fixture
def authenticated_user(client):
    unique_id = uuid4().hex

    payload = {
        "username": f"booking_user_{unique_id}",
        "email": f"booking_{unique_id}@gmail.com",
        "password": "Test@12345",
        "phone_no": str(uuid4().int % 10**10).zfill(10),
        "address": "Test Address",
        "city": "Kolhapur",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=payload
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": payload["email"],
            "password": payload["password"],
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "user": payload,
        "token": token,
    }


@pytest.fixture
def authenticated_admin(client):
    unique_id = uuid4().hex

    payload = {
        "username": f"admin_user_{unique_id}",
        "email": f"admin_{unique_id}@gmail.com",
        "password": "Admin@12345",
        "phone_no": str(uuid4().int % 10**10).zfill(10),
        "address": "Admin Test Address",
        "city": "Kolhapur",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=payload
    )

    assert register_response.status_code == 201

    db = TestingSessionLocal()

    try:
        from app.models.user import User, UserRole

        user = (
            db.query(User)
            .filter(User.email == payload["email"])
            .first()
        )

        assert user is not None

        user.role = UserRole.ADMIN

        db.commit()

    finally:
        db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": payload["email"],
            "password": payload["password"],
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "user": payload,
        "token": token,
    }