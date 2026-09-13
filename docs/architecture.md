\# System Architecture



\## 1. Overview



The Ticket Booking System follows a layered architecture designed to separate HTTP handling, business logic, persistence, and infrastructure concerns.



```text

Angular Frontend

&#x20;      │

&#x20;      │ REST / JSON

&#x20;      ▼

FastAPI Routes

&#x20;      │

&#x20;      ▼

Service Layer

&#x20;      │

&#x20;      ▼

Repository Layer

&#x20;      │

&#x20;      ▼

PostgreSQL

```



Redis and Razorpay operate as supporting infrastructure:



```text

&#x20;                   ┌───────────────┐

&#x20;                   │    Redis      │

&#x20;                   │ Seat Locks    │

&#x20;                   │ TTL           │

&#x20;                   └───────▲───────┘

&#x20;                           │

Angular → FastAPI → Services → Repositories → PostgreSQL

&#x20;                           │

&#x20;                           ▼

&#x20;                    ┌───────────────┐

&#x20;                    │   Razorpay    │

&#x20;                    │   Payments    │

&#x20;                    └───────────────┘

```



\---



\## 2. Architectural Layers



\### API Layer



The API layer is responsible for:



\* HTTP request handling

\* Request validation

\* Authentication dependencies

\* Authorization

\* Response serialization

\* HTTP status codes



The API layer should avoid implementing complex business rules directly.



\---



\### Service Layer



The service layer contains application and domain-level operations.



Examples include:



\* Booking creation

\* Seat reservation

\* Booking cancellation

\* Booking expiry

\* Payment creation

\* Event management

\* User administration



Services coordinate repositories and external infrastructure.



\---



\### Repository Layer



Repositories encapsulate database access.



Typical responsibilities include:



\* Querying entities

\* Creating records

\* Updating records

\* Filtering active reservations

\* Retrieving event/venue/seat relationships



This prevents SQLAlchemy-specific persistence logic from leaking into API handlers.



\---



\### Model Layer



SQLAlchemy models represent persistent domain entities.



Major entities include:



```text

User

Event

Venue

Seat

Booking

BookingSeat

Payment

EventVenue

```



\---



\### Schema Layer



Pydantic schemas define API input and output contracts.



This provides:



\* Request validation

\* Response serialization

\* Type safety at the API boundary

\* Separation between database models and API contracts



\---



\## 3. Authentication Flow



```text

User

&#x20;│

&#x20;▼

Login API

&#x20;│

&#x20;▼

Validate credentials

&#x20;│

&#x20;▼

Verify Argon2 password hash

&#x20;│

&#x20;▼

Generate JWT

&#x20;│

&#x20;▼

Client stores access token

&#x20;│

&#x20;▼

Protected API request

&#x20;│

&#x20;▼

JWT validation

&#x20;│

&#x20;▼

Current user

&#x20;│

&#x20;▼

Role authorization

```



Administrative endpoints additionally require the authenticated user to have the appropriate role.



\---



\## 4. Booking Architecture



Booking creation is intentionally more than a simple database insert.



```text

Client

&#x20; │

&#x20; ▼

Booking API

&#x20; │

&#x20; ▼

Authentication

&#x20; │

&#x20; ▼

Validate event / seats

&#x20; │

&#x20; ▼

Acquire Redis locks

&#x20; │

&#x20; ├───────────────┐

&#x20; │               │

Success         Failure

&#x20; │               │

&#x20; ▼               ▼

Create PENDING   Reject request

booking

&#x20; │

&#x20; ▼

Set expiration

&#x20; │

&#x20; ▼

Create payment order

&#x20; │

&#x20; ▼

Payment result

&#x20; │

&#x20; ├── Success ──► CONFIRMED

&#x20; │

&#x20; ├── Failure ──► PAYMENT\_FAILED

&#x20; │

&#x20; └── Timeout ──► CANCELLED

```



\---



\## 5. Redis Integration



Redis is not used as the permanent source of booking truth.



Instead:



```text

PostgreSQL

&#x20;   ↓

Persistent booking state



Redis

&#x20;   ↓

Temporary distributed coordination

```



A seat lock follows:



```text

seat\_lock:{event\_id}:{seat\_id}

```



The lock has a TTL and is acquired atomically.



This prevents multiple application instances from independently believing they own the same temporary reservation.



\---



\## 6. Database Responsibility



PostgreSQL remains the source of truth for:



\* Users

\* Events

\* Venues

\* Seats

\* Bookings

\* Booking seats

\* Payments

\* Event/venue relationships



Redis state is temporary and recoverable.



This distinction is important because losing a Redis lock should not destroy persistent booking information.



\---



\## 7. Event and Venue Relationship



Events and venues use a many-to-many relationship.



```text

Event

&#x20; │

&#x20; ▼

EventVenue

&#x20; │

&#x20; ▼

Venue

```



This allows an event to be offered at multiple venues.



For example:



```text

Event 1

&#x20;├── Venue 2

&#x20;├── Venue 4

&#x20;└── Venue 6

```



\---



\## 8. Seat Identity



Seat labels are scoped to venues.



For example:



```text

Venue 2 → A1 → seat\_id 100

Venue 4 → A1 → seat\_id 250

```



Although both seats are labelled `A1`, they are different database entities.



Booking one does not affect the other.



This is enforced through the relationship between:



```text

Seat → Venue

BookingSeat → Seat

Booking → Event

```



\---



\## 9. Payment Architecture



The payment subsystem stores the relationship between an internal booking and the external payment gateway.



```text

Booking

&#x20;  │

&#x20;  ▼

Payment

&#x20;  │

&#x20;  ├── Razorpay Order ID

&#x20;  ├── Razorpay Payment ID

&#x20;  ├── Amount

&#x20;  ├── Currency

&#x20;  └── Status

```



The external gateway identifier is persisted so that payment operations can be correlated with internal booking records.



\---



\## 10. Failure Handling



The architecture explicitly handles several failure cases.



\### Seat already reserved



Redis lock acquisition fails.



Result:



```text

409 Conflict

```



\### Payment failure



The payment is marked failed and the reservation can be released according to the booking lifecycle.



\### Abandoned booking



The pending booking expires and its associated seats are made available again.



\### Invalid authentication



The request is rejected before protected business logic is executed.



\### Unauthorized administration request



The request is rejected when the authenticated user does not have the required role.



\---



\## 11. Design Principles



The system follows several practical engineering principles:



\* Keep controllers thin.

\* Keep business logic in services.

\* Keep database access in repositories.

\* Keep persistent state in PostgreSQL.

\* Use Redis only where temporary distributed coordination is required.

\* Validate API inputs using schemas.

\* Protect sensitive configuration with environment variables.

\* Use database migrations instead of manually modifying production schemas.

\* Make concurrency behavior explicit and testable.



