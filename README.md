# Ticket Booking System

A backend-focused ticket booking platform designed around **concurrent seat reservation, transactional booking workflows, distributed locking, role-based access control, and payment processing**.

The system uses **Angular** for the client application, **FastAPI** for the REST API, **PostgreSQL** for transactional persistence, **Redis** for distributed seat locking and temporary reservation expiry, and **Razorpay** for payment processing.

> **Engineering focus:** preventing double-booking under concurrent requests while maintaining a clean separation between API, business logic, persistence, and infrastructure concerns.

---

## Highlights

- RESTful backend built with **FastAPI**
- Angular-based customer and administration interfaces
- PostgreSQL persistence using **SQLAlchemy**
- Database schema versioning with **Alembic**
- **Redis-based distributed seat locking**
- TTL-based temporary seat reservations
- Automatic expiry of abandoned pending bookings
- Transactional booking workflow
- Prevention of concurrent double-booking
- Role-based access control for `USER` and `ADMIN`
- JWT-based authentication
- Argon2 password hashing
- Razorpay payment integration
- Dockerized backend infrastructure
- Repository/service architecture
- Automated backend tests
- Dedicated concurrency/load-testing scripts
- Swagger/OpenAPI documentation through FastAPI

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      Angular UI      │
                         │                      │
                         │  Customer / Admin    │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP / JSON
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │ Routes / Auth / RBAC │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Service Layer     │
                         │                      │
                         │ Booking / Payment /  │
                         │ Event / User Logic   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴───────────┐
                         │                      │
                         ▼                      ▼
                ┌─────────────────┐    ┌─────────────────┐
                │ Repository      │    │ Redis           │
                │ Layer           │    │                 │
                │                 │    │ Distributed     │
                │ SQLAlchemy      │    │ Seat Locks      │
                └────────┬────────┘    │ TTL             │
                         │             └─────────────────┘
                         ▼
                ┌─────────────────┐
                │ PostgreSQL      │
                │                 │
                │ Users           │
                │ Events          │
                │ Venues          │
                │ Seats           │
                │ Bookings        │
                │ Payments        │
                └─────────────────┘

                         ┌─────────────────┐
                         │    Razorpay     │
                         │                 │
                         │ Payment Gateway │
                         └─────────────────┘
