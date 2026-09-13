from uuid import uuid4


def test_complete_booking_flow(
    client,
    authenticated_user,
    booking_test_data,
    monkeypatch
):
    token = authenticated_user["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    event = booking_test_data["event"]
    seat = booking_test_data["seat_2"]

    event_response = client.get(
        f"/api/v1/events/{event.id}",
        headers=headers
    )

    assert event_response.status_code == 200

    booking_response = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "event_id": event.id,
            "seat_ids": [seat.id]
        }
    )

    assert booking_response.status_code == 201

    booking_id = booking_response.json()["id"]

    assert booking_response.json()["status"] == "PENDING"

    fake_order_id = f"order_e2e_{uuid4().hex}"
    fake_payment_id = f"pay_e2e_{uuid4().hex}"

    class FakeOrder:

        def create(self, data):
            return {
                "id": fake_order_id
            }

    class FakeUtility:

        def verify_payment_signature(self, data):
            return None

    class FakeClient:

        def __init__(self, *args, **kwargs):
            self.order = FakeOrder()
            self.utility = FakeUtility()

    import razorpay

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

    assert order_data["razorpay_order_id"] == fake_order_id

    verify_response = client.post(
        "/api/v1/payments/verify",
        headers=headers,
        json={
            "razorpay_order_id": fake_order_id,
            "razorpay_payment_id": fake_payment_id,
            "razorpay_signature": "test_signature"
        }
    )

    assert verify_response.status_code == 200

    booking_get_response = client.get(
        f"/api/v1/bookings/{booking_id}",
        headers=headers
    )

    assert booking_get_response.status_code == 200

    booking_data = booking_get_response.json()

    assert booking_data["status"] == "CONFIRMED"