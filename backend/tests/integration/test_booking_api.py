def test_create_booking_success(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]
    seat_2 = booking_test_data["seat_2"]

    response = client.post(
        "/api/v1/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "event_id": event.id,
            "seat_ids": [
                seat_1.id,
                seat_2.id
            ]
        }
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 201

    data = response.json()

    assert data["event"]["id"] == event.id
    assert data["status"] == "PENDING"

    assert len(data["booking_seats"]) == 2

    seat_ids = {
        booking_seat["seat"]["id"]
        for booking_seat in data["booking_seats"]
    }

    assert seat_ids == {
        seat_1.id,
        seat_2.id
    }


def test_create_booking_already_booked_seat(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    first_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    print("FIRST STATUS:", first_response.status_code)
    print("SECOND STATUS:", second_response.status_code)
    print("SECOND BODY:", second_response.json())

    assert second_response.status_code == 409


def test_create_booking_without_authentication(
    client,
    booking_test_data
):
    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    response = client.post(
        "/api/v1/bookings",
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 401


def test_create_booking_with_invalid_seat_for_event(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    invalid_seat_id = 999999

    response = client.post(
        "/api/v1/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "event_id": event.id,
            "seat_ids": [invalid_seat_id]
        }
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 404


def test_create_booking_with_seat_from_different_venue(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    other_seat = booking_test_data["other_seat"]

    response = client.post(
        "/api/v1/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "event_id": event.id,
            "seat_ids": [other_seat.id]
        }
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 400


def test_get_my_bookings(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/bookings/me",
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["event"]["id"] == event.id


def test_cancel_booking(
    client,
    authenticated_user,
    booking_test_data
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert create_response.status_code == 201

    booking = create_response.json()
    booking_id = booking["id"]

    response = client.patch(
        f"/api/v1/bookings/{booking_id}/cancel",
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "CANCELLED"