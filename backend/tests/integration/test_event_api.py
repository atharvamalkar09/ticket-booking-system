from datetime import datetime, timedelta, timezone
from decimal import Decimal


def test_create_event(client, authenticated_admin, booking_test_data):
    token = authenticated_admin["token"]
    venue_id = booking_test_data["venue"].id

    start_time = datetime.now(timezone.utc) + timedelta(days=5)
    end_time = start_time + timedelta(hours=2)

    payload = {
        "title": "Integration Test Movie",
        "description": "Test event created through API",
        "category": "MOVIE",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "base_price": "300.00",
        "venue_ids": [venue_id]
    }

    response = client.post(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Integration Test Movie"
    assert data["category"] == "MOVIE"
    assert Decimal(str(data["base_price"])) == Decimal("300.00")
    assert len(data["venues"]) == 1
    assert data["venues"][0]["id"] == venue_id


def test_create_event_with_multiple_venues(
    client,
    authenticated_admin,
    booking_test_data
):
    token = authenticated_admin["token"]

    venue_1 = booking_test_data["venue"]
    venue_2 = booking_test_data["other_venue"]

    start_time = datetime.now(timezone.utc) + timedelta(days=7)
    end_time = start_time + timedelta(hours=2)

    payload = {
        "title": "Multi Venue Integration Event",
        "description": "Event available at multiple venues",
        "category": "MOVIE",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "base_price": "350.00",
        "venue_ids": [venue_1.id, venue_2.id]
    }

    response = client.post(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Multi Venue Integration Event"

    returned_venue_ids = {
        venue["id"]
        for venue in data["venues"]
    }

    assert returned_venue_ids == {
        venue_1.id,
        venue_2.id
    }