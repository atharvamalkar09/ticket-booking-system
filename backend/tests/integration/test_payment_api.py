from uuid import uuid4

import razorpay


def test_create_payment_order(
    client,
    authenticated_user,
    booking_test_data,
    monkeypatch
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    booking_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]

    class FakeOrder:
        def create(self, data):
            return {
                "id": f"order_test_{uuid4().hex}"
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.order = FakeOrder()

    monkeypatch.setattr(
        razorpay,
        "Client",
        FakeClient
    )

    response = client.post(
        f"/api/v1/payments/create-order/{booking_id}",
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 201

    data = response.json()

    assert data["razorpay_order_id"].startswith("order_test_")
    assert data["amount_in_paise"] == 25000
    assert data["currency"] == "INR"
    assert data["payment_id"] is not None


def test_verify_successful_payment(
    client,
    authenticated_user,
    booking_test_data,
    monkeypatch
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]
    payment_id = f"pay_test_success_{uuid4().hex}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    booking_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]

    class FakeOrder:
        def create(self, data):
            return {
                "id": f"order_test_success_{uuid4().hex}"
            }

    class FakeUtility:
        def verify_payment_signature(self, data):
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.order = FakeOrder()
            self.utility = FakeUtility()

    monkeypatch.setattr(
        razorpay,
        "Client",
        FakeClient
    )

    order_response = client.post(
        f"/api/v1/payments/create-order/{booking_id}",
        headers=headers
    )

    assert order_response.status_code == 201

    order_data = order_response.json()

    verify_response = client.post(
        "/api/v1/payments/verify",
        headers=headers,
        json={
            "razorpay_order_id": order_data["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": "test_signature"
        }
    )

    print("STATUS:", verify_response.status_code)
    print("BODY:", verify_response.json())

    assert verify_response.status_code == 200

    payment_data = verify_response.json()

    assert payment_data["status"] == "SUCCESS"

    booking_check = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=headers
    )

    assert booking_check.status_code == 200
    assert booking_check.json()["status"] == "CONFIRMED"


def test_payment_failed_webhook(
    client,
    authenticated_user,
    booking_test_data,
    monkeypatch
):
    token = authenticated_user["token"]

    event = booking_test_data["event"]
    seat_1 = booking_test_data["seat_1"]

    auth_headers = {
        "Authorization": f"Bearer {token}"
    }

    booking_response = client.post(
        "/api/v1/bookings",
        headers=auth_headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat_1.id]
        }
    )

    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]

    class FakeOrder:
        def create(self, data):
            return {
                "id": f"order_test_failed_{uuid4().hex}"
            }

    class FakeUtility:
        def verify_webhook_signature(
            self,
            body,
            signature,
            secret
        ):
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.order = FakeOrder()
            self.utility = FakeUtility()

    monkeypatch.setattr(
        razorpay,
        "Client",
        FakeClient
    )

    order_response = client.post(
        f"/api/v1/payments/create-order/{booking_id}",
        headers=auth_headers
    )

    assert order_response.status_code == 201

    order_data = order_response.json()

    webhook_payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_failed",
                    "order_id": order_data["razorpay_order_id"]
                }
            }
        }
    }

    response = client.post(
        "/api/v1/payments/webhook",
        headers={
            "X-Razorpay-Signature": "test_webhook_signature"
        },
        json=webhook_payload
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "processed"
    assert data["event"] == "payment.failed"
    assert data["booking_id"] == booking_id
    assert data["payment_status"] == "FAILED"

    booking_check = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=auth_headers
    )

    assert booking_check.status_code == 200

    booking_data = booking_check.json()

    assert booking_data["status"] == "PAYMENT_FAILED"