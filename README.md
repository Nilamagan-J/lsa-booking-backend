# HabotConnect — LSA Booking Backend

A Django REST API for managing Learning Support Assistant (LSA) bookings, availability, and payment processing.

This project was developed as a backend evaluation project demonstrating Python, Django, Django REST Framework, PostgreSQL, REST API design, validation, database relationships, query optimization, external HTTP integration, error handling, logging, automated testing, GitHub Actions CI, and documentation.

## Features

* Parent management
* Learning Support Assistant (LSA) profiles
* Booking creation
* Booking time validation
* Double-booking prevention
* LSA availability filtering
* PostgreSQL database
* Payment service integration
* Payment webhook
* Payment failure handling
* Timeout handling
* Application logging
* Database query optimization
* Automated tests with pytest
* GitHub Actions CI

## Technology Stack

* Python 3.12
* Django 5.2
* Django REST Framework
* PostgreSQL 16
* psycopg
* requests
* python-dotenv
* pytest
* pytest-django
* Git
* GitHub Actions

## Project Structure

```text
lsa-booking-backend/
├── .github/
│   └── workflows/
│       └── tests.yml
├── bookings/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_models.py
│   │   ├── test_bookings.py
│   │   └── test_payments.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Database Design

The application contains four main entities:

```text
Parent 1 ─────────── * Booking * ─────────── 1 LSAProfile
                         │
                         │ 1
                         │
                         ▼
                       Payment
```

### Parent

Stores the parent requesting support.

### LSAProfile

Stores information about a Learning Support Assistant, including:

* name
* email
* specialization
* hourly rate
* availability

### Booking

Connects a Parent with an LSA and stores:

* booking date
* start time
* end time
* status
* notes
* timestamps

### Payment

Stores payment information associated with a booking:

* amount
* status
* transaction ID
* timestamps

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=lsa_booking_db
DB_USER=lsa_backend
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

PAYMENT_API_URL=http://127.0.0.1:8000/api/mock-payment/
PAYMENT_API_TIMEOUT=5
```

The `.env` file contains local configuration and must not be committed to Git.

A `.env.example` file is included in the repository to show the required environment variables without exposing actual credentials.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd lsa-booking-backend
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure PostgreSQL and create the database/user specified in `.env`.

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

## API Endpoints

### Create Booking

```http
POST /api/v1/bookings/
```

Example request:

```json
{
    "parent": 1,
    "lsa": 1,
    "booking_date": "2026-08-16",
    "start_time": "14:00:00",
    "end_time": "15:00:00",
    "notes": "Mathematics support"
}
```

A successful request creates a booking and initiates payment.

### List Available LSAs

```http
GET /api/v1/lsa/resources/
```

Filter by specialization:

```http
GET /api/v1/lsa/resources/?skill=Autism
```

### Payment Webhook

```http
POST /api/v1/payments/webhook/
```

Example request:

```json
{
    "transaction_id": "txn_example",
    "status": "success"
}
```

## Booking Validation

The API validates:

* Parent existence
* LSA existence
* booking time range
* booking conflicts
* required fields

Overlapping bookings for the same LSA are rejected.

## Payment Integration

The payment integration uses the Python `requests` library.

The payment service:

1. Reads payment configuration from environment variables.
2. Sends booking information to the payment service.
3. Uses a timeout to prevent indefinite waiting.
4. Handles HTTP and request errors.
5. Handles invalid JSON responses.
6. Validates the payment response.
7. Returns the transaction ID and payment status.

Payment failures are converted into application-level errors instead of exposing low-level HTTP exceptions to the API client.

## Webhook Processing

The payment webhook receives a transaction ID and payment status.

For a successful payment:

```text
Payment → success
Booking → confirmed
```

For a failed payment:

```text
Payment → failed
Booking → cancelled
```

The webhook uses `select_related("booking")` to efficiently retrieve the related booking.

## Query Optimization

The booking conflict query frequently filters by LSA and booking date.

A composite database index was added for:

```text
(lsa, booking_date)
```

The payment webhook uses:

```python
select_related("booking")
```

to efficiently retrieve the related booking and avoid unnecessary additional queries.

## Logging

The payment service uses Python's logging framework to record important events such as:

* payment initiation
* successful payment requests
* timeouts
* HTTP/request failures
* invalid responses
* unexpected payment responses

Sensitive credentials are not logged.

## Testing

The project uses:

* pytest
* pytest-django

Run the test suite:

```bash
pytest
```

The test suite covers:

* model relationships
* successful booking creation
* invalid booking time
* overlapping bookings
* LSA resource listing
* LSA specialization filtering
* unknown specialization filtering
* successful payment
* payment service failure
* successful payment webhook
* invalid webhook status
* unknown payment transaction

Current result:

```text
12 passed
```

## Continuous Integration

GitHub Actions runs automatically on pushes and pull requests to `main`.

The CI pipeline:

1. Checks out the repository.
2. Installs Python.
3. Starts PostgreSQL.
4. Installs project dependencies.
5. Runs Django migrations.
6. Runs pytest.

The workflow is located at:

```text
.github/workflows/tests.yml
```

## Error Handling

The application handles:

* invalid input
* missing database objects
* booking conflicts
* invalid payment responses
* payment HTTP errors
* payment timeouts
* unknown webhook transactions
* invalid webhook statuses

The API returns controlled HTTP responses rather than exposing internal exceptions.

## Development

Run Django checks:

```bash
python manage.py check
```

Run tests:

```bash
pytest
```

Run the development server:

```bash
python manage.py runserver
```

## Project Goal

The goal of this project is to demonstrate a clean and maintainable Django backend with relational database design, REST APIs, validation, external service integration, testing, logging, query optimization, CI/CD, and clear technical documentation.
