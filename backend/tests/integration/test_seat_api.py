def test_create_seat(
    client,
    authenticated_admin,
    booking_test_data
):
    token = authenticated_admin["token"]

    venue_id = booking_test_data["venue"].id

    payload = {
        "venue_id": venue_id,
        "row": "Z",
        "number": 1,
        "category": "STANDARD"
    }

    response = client.post(
        "/api/v1/seats",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["venue_id"] == venue_id
    assert data["row"] == "Z"
    assert data["number"] == 1
    assert data["category"] == "STANDARD"


def test_duplicate_seat_rejected(
    client,
    authenticated_admin,
    booking_test_data
):
    token = authenticated_admin["token"]

    venue_id = booking_test_data["venue"].id

    # First seat
    payload = {
        "venue_id": venue_id,
        "row": "Y",
        "number": 1,
        "category": "STANDARD"
    }

    first_response = client.post(
        "/api/v1/seats",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload
    )

    assert first_response.status_code == 201

    # Duplicate seat
    duplicate_response = client.post(
        "/api/v1/seats",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload
    )

    assert duplicate_response.status_code in (400, 409)