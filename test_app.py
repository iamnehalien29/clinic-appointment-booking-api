
import pytest

import db
import app as clinic_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_clinic.db"

    monkeypatch.setattr(db, "DATABASE", str(test_database))
    db.init_db()

    clinic_app.app.config["TESTING"] = True

    with clinic_app.app.test_client() as client:
        yield client


def create_slot(client):
    return client.post(
        "/slots",
        json={
            "clinic_id": "clinic_001",
            "starts_at": "2026-11-01T10:00:00",
            "ends_at": "2026-11-01T10:30:00",
        },
    )


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_create_slot(client):
    response = create_slot(client)

    assert response.status_code == 201
    assert response.json["slot"]["status"] == "available"


def test_book_slot(client):
    slot_response = create_slot(client)
    slot_id = slot_response.json["slot"]["id"]

    response = client.post(
        "/bookings",
        json={
            "slot_id": slot_id,
            "patient_name": "Rahul Sharma",
            "patient_email": "rahul@example.com",
        },
    )

    assert response.status_code == 201
    assert response.json["booking"]["status"] == "confirmed"


def test_prevent_double_booking(client):
    slot_response = create_slot(client)
    slot_id = slot_response.json["slot"]["id"]

    booking_data = {
        "slot_id": slot_id,
        "patient_name": "Rahul Sharma",
        "patient_email": "rahul@example.com",
    }

    first = client.post("/bookings", json=booking_data)
    second = client.post("/bookings", json=booking_data)

    assert first.status_code == 201
    assert second.status_code == 409


def test_cancel_booking_releases_slot(client):
    slot_response = create_slot(client)
    slot_id = slot_response.json["slot"]["id"]

    booking_response = client.post(
        "/bookings",
        json={
            "slot_id": slot_id,
            "patient_name": "Rahul Sharma",
            "patient_email": "rahul@example.com",
        },
    )
    booking_id = booking_response.json["booking"]["id"]

    cancel_response = client.delete(f"/bookings/{booking_id}")

    assert cancel_response.status_code == 200

    slots_response = client.get("/slots")
    assert slots_response.json["slots"][0]["status"] == "available"

    bookings_response = client.get("/bookings")
    assert bookings_response.json["bookings"][0]["status"] == "cancelled"


def test_missing_slot_returns_not_found(client):
    response = client.post(
        "/bookings",
        json={
            "slot_id": 999,
            "patient_name": "Rahul Sharma",
            "patient_email": "rahul@example.com",
        },
    )

    assert response.status_code == 404

def test_create_slot_rejects_invalid_date(client):
    response = client.post(
        "/slots",
        json={
            "clinic_id": "clinic_001",
            "starts_at": "2026-13-45T10:00:00",
            "ends_at": "2026-11-01T10:30:00",
        },
    )

    assert response.status_code == 400
    assert "ISO 8601" in response.json["error"]

def test_create_slot_rejects_missing_fields(client):
    response = client.post(
        "/slots",
        json={
            "clinic_id": "clinic_001",
            "starts_at": "2026-11-01T10:00:00",
        },
    )

    assert response.status_code == 400
    assert "required" in response.json["error"]


def test_cannot_cancel_booking_twice(client):
    slot_response = create_slot(client)
    slot_id = slot_response.json["slot"]["id"]

    booking_response = client.post(
        "/bookings",
        json={
            "slot_id": slot_id,
            "patient_name": "Rahul Sharma",
            "patient_email": "rahul@example.com",
        },
    )

    booking_id = booking_response.json["booking"]["id"]

    first_cancel = client.delete(f"/bookings/{booking_id}")
    second_cancel = client.delete(f"/bookings/{booking_id}")

    assert first_cancel.status_code == 200
    assert second_cancel.status_code == 409
