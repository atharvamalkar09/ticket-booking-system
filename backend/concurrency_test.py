import asyncio
import httpx

API_URL = "http://localhost:8000/api/v1/bookings"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwicm9sZSI6IlVTRVIiLCJleHAiOjE3ODg5NTE5MzR9.iNytJISVaJXu4wD9r5BjRQl18dKbVqr8FTZfqI_z0Z8"

EVENT_ID = 1
SEAT_ID = 67

NUMBER_OF_REQUESTS = 20


async def attempt_booking(client, request_number):
    payload = {
        "event_id": EVENT_ID,
        "seat_ids": [SEAT_ID]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    try:
        response = await client.post(
            API_URL,
            json=payload,
            headers=headers
        )

        return {
            "request": request_number,
            "status_code": response.status_code,
            "body": response.json()
        }

    except Exception as e:
        return {
            "request": request_number,
            "status_code": "ERROR",
            "body": str(e)
        }


async def main():

    async with httpx.AsyncClient(timeout=30.0) as client:

        tasks = [
            attempt_booking(client, i)
            for i in range(1, NUMBER_OF_REQUESTS + 1)
        ]

        results = await asyncio.gather(*tasks)

    print("\n========== RESULTS ==========\n")

    success_count = 0
    conflict_count = 0
    other_count = 0

    for result in results:

        print(
    f"Request {result['request']:02d} → "
    f"{result['status_code']} → {result['body']}"
        )

        if result["status_code"] == 201:
            success_count += 1

        elif result["status_code"] in (400, 409):
            conflict_count += 1

        else:
            other_count += 1

    print("\n========== SUMMARY ==========\n")

    print(f"Total requests : {NUMBER_OF_REQUESTS}")
    print(f"Successful     : {success_count}")
    print(f"Conflicts      : {conflict_count}")
    print(f"Other          : {other_count}")

    print("\nExpected:")
    print("Successful     : 1")
    print(f"Conflicts      : {NUMBER_OF_REQUESTS - 1}")
    print("Double booking : 0")


if __name__ == "__main__":
    asyncio.run(main())