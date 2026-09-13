\# Concurrency and Seat Reservation



\## 1. Problem



Ticket booking introduces a classic concurrency problem.



Suppose two users attempt to reserve the same seat at nearly the same time:



```text

User A ──────┐

&#x20;            ├──► Seat A1

User B ──────┘

```



The system must guarantee that both requests cannot successfully reserve the same seat.



The critical requirement is:



> For a given event and seat, concurrent requests must result in at most one successful temporary reservation.



\---



\## 2. Why a Distributed Lock?



The application uses Redis to coordinate temporary seat ownership.



The Redis lock is useful because:



\* Redis provides atomic operations.

\* Lock acquisition is fast.

\* TTL automatically releases abandoned locks.

\* The approach works across multiple API processes/instances.



PostgreSQL remains the persistent source of truth.



\---



\## 3. Lock Key



Each event-seat combination gets a unique Redis key:



```text

seat\_lock:{event\_id}:{seat\_id}

```



For example:



```text

seat\_lock:1:62

```



This means:



```text

Event 1

Seat 62

```



is temporarily reserved.



\---



\## 4. Atomic Acquisition



The lock is acquired using an atomic Redis operation with `NX`.



Conceptually:



```text

SET seat\_lock:1:62 <booking\_id> NX EX 300

```



The important properties are:



\* `NX`: only create the key if it does not already exist.

\* `EX 300`: automatically expire the lock after 300 seconds.



Therefore, two concurrent requests cannot both successfully create the same lock.



\---



\## 5. Successful Request



```text

Request A

&#x20;  │

&#x20;  ▼

Acquire Redis lock

&#x20;  │

&#x20;  ▼

SUCCESS

&#x20;  │

&#x20;  ▼

Create PENDING booking

&#x20;  │

&#x20;  ▼

Continue payment workflow

```



\---



\## 6. Conflicting Request



```text

Request B

&#x20;  │

&#x20;  ▼

Acquire Redis lock

&#x20;  │

&#x20;  ▼

Lock already exists

&#x20;  │

&#x20;  ▼

Reject request

&#x20;  │

&#x20;  ▼

409 Conflict

```



The second request does not proceed as though it owns the seat.



\---



\## 7. Lock Ownership



The Redis value contains the booking identifier.



This is important when releasing a lock.



The system does not blindly execute:



```text

DEL seat\_lock:1:62

```



Instead, the release operation verifies that the lock belongs to the expected booking before deleting it.



Conceptually:



```text

IF lock.value == booking\_id

&#x20;   DELETE lock

```



This prevents one booking from accidentally releasing another booking's lock.



\---



\## 8. Reservation Expiry



A temporary booking is assigned an expiration timestamp:



```text

booking.expires\_at

```



The Redis lock also has a TTL.



The two mechanisms provide complementary protection:



```text

Redis TTL

&#x20;   ↓

Temporary distributed lock expires



Database expires\_at

&#x20;   ↓

Persistent booking state becomes expired

```



This prevents abandoned checkout sessions from permanently consuming seat inventory.



\---



\## 9. Booking State



The booking lifecycle is:



```text

PENDING

&#x20;  │

&#x20;  ├── Payment success ──► CONFIRMED

&#x20;  │

&#x20;  ├── Payment failure ─► PAYMENT\_FAILED

&#x20;  │

&#x20;  └── Expiry ───────────► CANCELLED

```



Booking seats associated with expired/cancelled reservations are no longer considered active.



\---



\## 10. Active Seat Logic



A seat is treated as unavailable when it is associated with an active booking.



For pending bookings, the reservation must also still be valid:



```text

status = PENDING

AND

expires\_at > current\_time

```



Confirmed bookings remain active until the booking is otherwise cancelled according to the application's lifecycle.



\---



\## 11. Concurrency Test: Same Seat



The system was tested with 100 concurrent requests targeting the same event and seat.



Observed result:



| Metric                  | Result |

| ----------------------- | -----: |

| Requests                |    100 |

| Successful reservations |      1 |

| Conflicts               |     99 |

| Server errors           |      0 |



One recorded local run produced approximately:



```text

Requests/sec : 54.42

Average latency : 1647 ms

```



The primary correctness result is:



```text

100 attempts

&#x20;    ↓

1 successful reservation

99 rejected attempts

0 server errors

```



This demonstrates that the locking mechanism prevented duplicate successful reservations during the test.



\---



\## 12. Concurrency Test: Unique Seats



A second test sent 50 concurrent requests targeting different seats.



Observed result:



| Metric              | Result |

| ------------------- | -----: |

| Requests            |     50 |

| Successful requests |     50 |

| Errors              |      0 |



Recorded throughput:



```text

\~25.77 requests/sec

```



\---



\## 13. Benchmark Interpretation



These tests are functional concurrency tests performed in a local development environment.



They are \*\*not production capacity benchmarks\*\*.



The tests primarily validate:



1\. Mutual exclusion for the same seat.

2\. Absence of duplicate successful reservations.

3\. Correct conflict handling.

4\. Behavior under simultaneous requests.

5\. Ability to reserve independent seats concurrently.



Production benchmarking would require controlled infrastructure, representative workloads, database tuning, network latency, multiple API instances, and observability.



\---



\## 14. Concurrency Design Principle



The system separates two responsibilities:



```text

Redis

─────

Fast temporary coordination



PostgreSQL

──────────

Durable business state

```



This avoids treating Redis as the permanent booking database while still using it where distributed coordination provides value.



\---



\## 15. Future Improvements



Potential improvements for a larger production deployment include:



\* Idempotency keys for booking requests.

\* Payment webhook verification.

\* Distributed rate limiting.

\* Background workers for expiry processing.

\* Metrics for lock contention.

\* Redis monitoring.

\* Database query profiling.

\* Distributed tracing.

\* Multi-instance load testing.

\* Failure-injection testing.

\* More extensive integration testing.



