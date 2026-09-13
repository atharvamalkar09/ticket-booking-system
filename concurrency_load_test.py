import asyncio
import time
import statistics
import httpx


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://localhost:8000/api/v1/bookings"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4Iiwicm9sZSI6IlVTRVIiLCJleHAiOjE3ODkwNDI4NDR9.lgYFXKzdyBY_xNyvRgA7dT7W0og8572ysAgJlJzzWGw"

EVENT_ID = 1

# 50 AVAILABLE database seat IDs for venue 2
#
# Excluded already-booked seats:
# A6=7, A8=9, B6=17,
# C2=23, C3=24, C4=25, C10=31,
# D1=38, D2=39,
# F5=62
#

SEAT_IDS = [227] * 100
NUMBER_OF_REQUESTS = len(SEAT_IDS)

TIMEOUT = 60.0


# ============================================================
# BOOKING REQUEST
# ============================================================

async def attempt_booking(client, request_number):

    # Each request gets a DIFFERENT seat
    seat_id = SEAT_IDS[request_number - 1]

    payload = {
        "event_id": EVENT_ID,
        "seat_ids": [seat_id]
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    start_time = time.perf_counter()

    try:

        response = await client.post(
            API_URL,
            json=payload,
            headers=headers
        )

        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        try:
            body = response.json()
        except Exception:
            body = response.text

        return {
            "request": request_number,
            "seat_id": seat_id,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "body": body
        }

    except Exception as e:

        end_time = time.perf_counter()

        latency_ms = (end_time - start_time) * 1000

        return {
            "request": request_number,
            "seat_id": seat_id,
            "status_code": "ERROR",
            "latency_ms": latency_ms,
            "body": str(e)
        }


# ============================================================
# PERCENTILE
# ============================================================

def percentile(values, percentile):

    if not values:
        return 0

    values = sorted(values)

    index = (percentile / 100) * (len(values) - 1)

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return values[lower] + (values[upper] - values[lower]) * weight


# ============================================================
# MAIN
# ============================================================

async def main():

    print("\n========================================")
    print("       REDIS LOAD TEST")
    print("========================================")
    print(f"Event ID       : {EVENT_ID}")
    print(f"Requests       : {NUMBER_OF_REQUESTS}")
    print(f"Unique seats   : {len(set(SEAT_IDS))}")
    print("========================================\n")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        start_time = time.perf_counter()

        tasks = [
            attempt_booking(client, i)
            for i in range(1, NUMBER_OF_REQUESTS + 1)
        ]

        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()

    total_time = end_time - start_time

    # ========================================================
    # CLASSIFY RESULTS
    # ========================================================

    success_count = 0
    conflict_count = 0
    other_count = 0

    latencies = []

    for result in results:

        if result["status_code"] == 201:
            success_count += 1

        elif result["status_code"] in (400, 409):
            conflict_count += 1

        else:
            other_count += 1

        if result["status_code"] != "ERROR":
            latencies.append(result["latency_ms"])

    # ========================================================
    # PERFORMANCE METRICS
    # ========================================================

    requests_per_second = (
        NUMBER_OF_REQUESTS / total_time
        if total_time > 0
        else 0
    )

    average_latency = (
        statistics.mean(latencies)
        if latencies
        else 0
    )

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    # ========================================================
    # RESULTS
    # ========================================================

    print("\n========== PERFORMANCE ==========\n")

    print(f"Total time      : {total_time:.3f} seconds")
    print(f"Requests/sec    : {requests_per_second:.2f}")
    print(f"Average latency : {average_latency:.2f} ms")
    print(f"P50 latency     : {p50:.2f} ms")
    print(f"P95 latency     : {p95:.2f} ms")
    print(f"P99 latency     : {p99:.2f} ms")

    print("\n========== RESULTS ==========\n")

    print(f"Total requests  : {NUMBER_OF_REQUESTS}")
    print(f"Successful      : {success_count}")
    print(f"Conflicts       : {conflict_count}")
    print(f"Other errors    : {other_count}")

    # ========================================================
    # REQUEST DETAILS
    # ========================================================

    print("\n========== REQUEST DETAILS ==========\n")

    for result in results:

        print(
            f"Request {result['request']:03d} → "
            f"Seat {result['seat_id']:02d} → "
            f"{result['status_code']} → "
            f"{result['latency_ms']:.2f} ms"
        )

    # ========================================================
    # OTHER ERRORS
    # ========================================================

    if other_count > 0:

        print("\n========== OTHER ERRORS ==========\n")

        for result in results:

            if result["status_code"] not in (201, 400, 409):

                print(
                    f"Request {result['request']:03d} → "
                    f"Seat {result['seat_id']} → "
                    f"{result['status_code']} → "
                    f"{result['body']}"
                )

    # ========================================================
    # CORRECTNESS
    # ========================================================

    print("\n========== CORRECTNESS ==========\n")

    expected_success = NUMBER_OF_REQUESTS
    expected_conflicts = 0

    print(f"Expected success   : {expected_success}")
    print(f"Expected conflicts : {expected_conflicts}")

    if (
        success_count == expected_success
        and conflict_count == expected_conflicts
    ):
        print("\n✓ CONCURRENCY CORRECTNESS PASSED")

    else:
        print("\n✗ CONCURRENCY CORRECTNESS FAILED")


if __name__ == "__main__":
    asyncio.run(main())