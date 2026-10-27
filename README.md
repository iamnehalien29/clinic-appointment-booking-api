# Clinic Appointment Booking API

A REST API built with Python, Flask, and SQLite that allows clinics to publish appointment slots and patients to book or cancel appointments.

## Features

- Create appointment slots for clinics.
- List available and booked appointment slots.
- Book an appointment slot.
- Prevent double booking of the same slot.
- Cancel an existing booking and release the slot.
- Validate request data and date-time values.
- Return meaningful HTTP error responses.
- Store appointment and booking data in SQLite.
- Run automated API tests using pytest.

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** SQLite
- **Testing:** pytest
- **Tools:** VS Code, Git, GitHub

## Project Structure

```text
clinic-booking-api/
├── app.py
├── db.py
├── test_app.py
├── clinic.db
├── .gitignore
├── README.md
└── .venv/
```

## Requirements

- Python 3.10 or newer
- pip

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd clinic-booking-api
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Git Bash on Windows:**

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
python -m pip install Flask pytest
```

### 5. Start the API

```bash
python app.py
```

The API will run at:

`http://127.0.0.1:5000`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/slots` | Create an appointment slot |
| GET | `/slots` | List appointment slots |
| POST | `/bookings` | Book an appointment |
| GET | `/bookings` | List bookings |
| DELETE | `/bookings/<booking_id>` | Cancel a booking |

## Example Requests

### Create an appointment slot

**POST** `/slots`

```json
{
  "clinic_id": "clinic_001",
  "starts_at": "2026-11-01T10:00:00",
  "ends_at": "2026-11-01T10:30:00"
}
```

### Book an appointment

**POST** `/bookings`

```json
{
  "slot_id": 1,
  "patient_name": "Rahul Sharma",
  "patient_email": "rahul@example.com"
}
```

### Cancel a booking

**DELETE** `/bookings/1`

Replace `1` with the booking ID returned by the API.

## Error Handling

The API uses HTTP status codes to communicate outcomes:

- `200 OK` — Request completed successfully.
- `201 Created` — Appointment slot or booking created.
- `400 Bad Request` — Invalid or missing input.
- `404 Not Found` — Requested slot or booking does not exist.
- `409 Conflict` — Slot is unavailable or booking is already cancelled.
- `500 Internal Server Error` — Unexpected server-side failure.

## Run Tests

Run the automated tests with:

```bash
python -m pytest -v
```

The tests cover health checks, slot creation, booking, double-booking prevention, cancellation, missing slots, invalid dates, missing fields, and repeated cancellation.

## Future Improvements

- Add patient and clinic authentication.
- Improve email validation.
- Add appointment search and filtering.
- Add timezone-aware scheduling rules.
- Add API documentation using Swagger or OpenAPI.
- Deploy the API to a cloud platform.

## Disclaimer

This is an educational project. It is not intended to store real patient information or be used as a production healthcare system without additional security, privacy, authentication, and reliability measures.