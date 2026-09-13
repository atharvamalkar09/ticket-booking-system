from uuid import uuid4


def test_create_venue(
    client,
    authenticated_admin
):
    token = authenticated_admin["token"]

    unique_id = uuid4().hex[:8]

    payload = {
        "name": f"Integration Test Cinema {unique_id}",
        "location": "Kolhapur",
        "capacity": 200,
        "description": "Integration test cinema"
    }

    response = client.post(
        "/api/v1/venues",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["location"] == "Kolhapur"
    assert data["capacity"] == 200