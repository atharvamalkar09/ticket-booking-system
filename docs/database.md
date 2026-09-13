\# Database Design



\## 1. Overview



PostgreSQL is the persistent source of truth for the application.



The database stores users, events, venues, seats, bookings, booking-seat relationships, payments, and event/venue mappings.



SQLAlchemy is used as the ORM and Alembic manages schema migrations.



\---



\## 2. Core Entities



```text

User

&#x20;│

&#x20;└──────────────► Booking

&#x20;                      │

&#x20;                      ├────────► BookingSeat ───────► Seat ───────► Venue

&#x20;                      │

&#x20;                      └────────► Payment



Event

&#x20;│

&#x20;└──────────────► EventVenue ◄──────────────────────── Venue

```



\---



\## 3. User



The `users` table represents application users.



Important attributes include:



\* User ID

\* Name

\* Email

\* Password hash

\* Role

\* Active/inactive state



Roles include:



```text

USER

ADMIN

```



Passwords are stored as Argon2 hashes rather than plaintext credentials.



\---



\## 4. Event



Events contain the information required to present a bookable event.



Current event attributes include:



```text

id

title

description

category

start\_time

end\_time

base\_price

```



An event does not directly contain a `venue\_id`.



Instead, the event/venue relationship is modeled separately.



\---



\## 5. Venue



A venue represents a physical location where an event can take place.



Important attributes include:



```text

id

name

location

capacity

```



The capacity represents the intended maximum inventory for the venue.



\---



\## 6. EventVenue



The `event\_venues` relationship supports many-to-many event scheduling.



Conceptually:



```text

Event A ───── Venue 1

&#x20;       ├──── Venue 2

&#x20;       └──── Venue 3



Event B ───── Venue 2

&#x20;       └──── Venue 4

```



This allows the same venue to host multiple events and an event to be associated with multiple venues.



\---



\## 7. Seat



Seats belong to a venue.



Important attributes include:



```text

id

venue\_id

row

number

category

```



Seat categories include:



```text

STANDARD

PREMIUM

VIP

```



Seat labels are generated from row and number values.



For example:



```text

A1

A2

A3

B1

B2

```



\---



\## 8. Seat Identity Across Venues



Seat labels are not globally unique.



For example:



```text

Venue 2

&#x20;   A1 → seat\_id 10



Venue 4

&#x20;   A1 → seat\_id 150

```



These represent two different physical seats.



The database uses the seat's primary key and venue relationship to maintain this distinction.



This is important because a booking for:



```text

Venue 2 / A1

```



must not mark:



```text

Venue 4 / A1

```



as unavailable.



This behavior has been verified end-to-end in the application.



\---



\## 9. Booking



A booking represents a user's reservation for an event.



Important fields include:



```text

id

user\_id

event\_id

status

total\_amount

expires\_at

created\_at

```



Booking statuses include:



```text

PENDING

CONFIRMED

CANCELLED

PAYMENT\_FAILED

```



\---



\## 10. BookingSeat



`booking\_seats` represents the seats associated with a booking.



Important fields include:



```text

id

booking\_id

event\_id

seat\_id

price

is\_active

```



The explicit `seat\_id` reference ensures that booking state is tied to the actual database seat identity rather than only to a display label.



\---



\## 11. Payment



The payment table connects an internal booking to an external payment gateway transaction.



Important fields include:



```text

id

booking\_id

razorpay\_order\_id

razorpay\_payment\_id

amount

currency

status

created\_at

updated\_at

```



Payment statuses include:



```text

CREATED

SUCCESS

FAILED

REFUNDED

```



The Razorpay payment ID can remain nullable until the gateway returns a successful payment identifier.



\---



\## 12. Booking and Payment Relationship



A booking can have its corresponding payment record.



Conceptually:



```text

Booking

&#x20;  │

&#x20;  └── Payment

&#x20;         │

&#x20;         ├── Razorpay Order ID

&#x20;         └── Razorpay Payment ID

```



The booking and payment states are maintained separately so that the application can distinguish between reservation state and payment state.



\---



\## 13. Reservation Expiry



Pending bookings have:



```text

expires\_at

```



This value represents the point at which a temporary reservation should no longer prevent the seats from being booked.



The application uses this value when determining whether a pending booking is still active.



\---



\## 14. Migration Management



Alembic is used for database schema versioning.



Migration history is stored in:



```text

backend/alembic/versions/

```



Typical workflow:



```bash

alembic revision --autogenerate -m "description"

alembic upgrade head

```



Rollback:



```bash

alembic downgrade -1

```



Database schema changes should be represented through migrations rather than manual production changes.



\---



\## 15. Data Integrity



The application separates:



```text

Event identity

Venue identity

Seat identity

Booking identity

Payment identity

```



This prevents UI-level labels such as `A1` from being treated as unique global identifiers.



Persistent booking state remains in PostgreSQL, while Redis is used only for temporary distributed locking.



\---



\## 16. Database Responsibilities



PostgreSQL is responsible for durable state.



Redis is responsible for temporary coordination.



```text

&#x20;                 ┌──────────────────────┐

&#x20;                 │      PostgreSQL      │

&#x20;                 │                      │

&#x20;                 │ Durable application  │

&#x20;                 │ state                │

&#x20;                 └──────────────────────┘



&#x20;                 ┌──────────────────────┐

&#x20;                 │        Redis         │

&#x20;                 │                      │

&#x20;                 │ Temporary seat locks │

&#x20;                 │ TTL                  │

&#x20;                 └──────────────────────┘

```



This separation allows the application to recover from expired temporary locks without treating Redis as the authoritative booking store.



