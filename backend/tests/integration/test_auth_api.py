from uuid import uuid4


def unique_phone():
    return str(uuid4().int % 10**10).zfill(10)


def test_register_user(client):
    unique_id = uuid4().hex

    payload = {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@gmail.com",
        "password": "Test@12345",
        "phone_no": unique_phone(),
        "address": "Test Address",
        "city": "Kolhapur",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]

    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    unique_id = uuid4().hex[:8]

    payload = {
        "username": f"duplicate_{unique_id}",
        "email": f"duplicate_{unique_id}@gmail.com",
        "password": "Test@12345",
        "phone_no": unique_phone(),
        "address": "Test Address",
        "city": "Kolhapur",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload
    )

    assert first_response.status_code == 201

    duplicate_payload = {
        **payload,
        "username": f"another_{unique_id}",
        "phone_no": unique_phone(),
    }

    second_response = client.post(
        "/api/v1/auth/register",
        json=duplicate_payload
    )

    assert second_response.status_code in (400, 409)


def test_login_success(client):
    unique_id = uuid4().hex[:8]

    registration_payload = {
        "username": f"login_{unique_id}",
        "email": f"login_{unique_id}@gmail.com",
        "password": "Test@12345",
        "phone_no": unique_phone(),
        "address": "Test Address",
        "city": "Kolhapur",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=registration_payload
    )

    assert register_response.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registration_payload["email"],
            "password": registration_payload["password"],
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    unique_id = uuid4().hex[:8]

    registration_payload = {
        "username": f"invalid_{unique_id}",
        "email": f"invalid_{unique_id}@gmail.com",
        "password": "Test@12345",
        "phone_no": unique_phone(),
        "address": "Test Address",
        "city": "Kolhapur",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=registration_payload
    )

    assert register_response.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registration_payload["email"],
            "password": "WrongPassword@123",
        }
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.get(
        "/api/v1/bookings/me"
    )

    assert response.status_code == 401