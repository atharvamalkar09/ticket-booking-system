def test_admin_can_access_admin_endpoint(
    client,
    authenticated_admin
):
    token = authenticated_admin["token"]

    response = client.get(
        "/api/v1/bookings/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_regular_user_cannot_access_admin_endpoint(
    client,
    authenticated_user
):
    token = authenticated_user["token"]

    response = client.get(
        "/api/v1/bookings/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_unauthenticated_user_cannot_access_admin_endpoint(
    client
):
    response = client.get(
        "/api/v1/bookings/admin"
    )

    assert response.status_code == 401