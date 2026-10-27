from datetime import datetime
from flask import Flask, jsonify, request
from db import get_db_connection, init_db

app = Flask(__name__)

# Create database tables when the app starts
init_db()


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Clinic Booking API is running"
    })


@app.route("/slots", methods=["POST"])
def create_slot():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    clinic_id = data.get("clinic_id")
    starts_at = data.get("starts_at")
    ends_at = data.get("ends_at")

    if not all([clinic_id, starts_at, ends_at]):
        return jsonify({
            "error": "clinic_id, starts_at, and ends_at are required"
        }), 400

    if not all(isinstance(value, str) for value in
               [clinic_id, starts_at, ends_at]):
        return jsonify({"error": "All fields must be strings"}), 400



    
    try:
        start_time = datetime.fromisoformat(starts_at)
        end_time = datetime.fromisoformat(ends_at)
    except ValueError:
        return jsonify({
            "error": "Dates must be valid ISO 8601 date-time strings"
        }), 400

    if start_time.tzinfo != end_time.tzinfo:
        return jsonify({
            "error": "Start and end times must use the same timezone format"
        }), 400

    if end_time <= start_time:
        return jsonify({
            "error": "ends_at must be later than starts_at"
        }), 400



    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO slots (clinic_id, starts_at, ends_at)
        VALUES (?, ?, ?)
        """,
        (clinic_id, starts_at, ends_at)
    )

    connection.commit()
    slot_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Appointment slot created successfully",
        "slot": {
            "id": slot_id,
            "clinic_id": clinic_id,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "status": "available"
        }
    }), 201

@app.route("/slots", methods=["GET"])
def list_slots():
    connection = get_db_connection()

    slots = connection.execute(
        """
        SELECT id, clinic_id, starts_at, ends_at, status
        FROM slots
        ORDER BY starts_at
        """
    ).fetchall()

    connection.close()

    return jsonify({
        "slots": [dict(slot) for slot in slots]
    }), 200

@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    slot_id = data.get("slot_id")
    patient_name = data.get("patient_name")
    patient_email = data.get("patient_email")

    if slot_id is None or not patient_name or not patient_email:
        return jsonify({
            "error": "slot_id, patient_name, and patient_email are required"
        }), 400

    if isinstance(slot_id, bool) or not isinstance(slot_id, int):
        return jsonify({"error": "slot_id must be an integer"}), 400

    if not isinstance(patient_name, str) or not patient_name.strip():
        return jsonify({"error": "patient_name must be a non-empty string"}), 400

    if not isinstance(patient_email, str) or "@" not in patient_email:
        return jsonify({"error": "A valid patient_email is required"}), 400

    connection = get_db_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        slot = connection.execute(
            "SELECT id, status FROM slots WHERE id = ?",
            (slot_id,)
        ).fetchone()

        if slot is None:
            connection.rollback()
            return jsonify({"error": "Appointment slot not found"}), 404

        if slot["status"] != "available":
            connection.rollback()
            return jsonify({"error": "Appointment slot is not available"}), 409

        cursor = connection.execute(
            """
            INSERT INTO bookings (slot_id, patient_name, patient_email)
            VALUES (?, ?, ?)
            """,
            (slot_id, patient_name.strip(), patient_email.strip())
        )

        connection.execute(
            "UPDATE slots SET status = 'booked' WHERE id = ?",
            (slot_id,)
        )

        connection.commit()

        return jsonify({
            "message": "Appointment booked successfully",
            "booking": {
                "id": cursor.lastrowid,
                "slot_id": slot_id,
                "patient_name": patient_name.strip(),
                "patient_email": patient_email.strip(),
                "status": "confirmed"
            }
        }), 201

    except Exception:
        connection.rollback()
        app.logger.exception("Failed to create booking")
        return jsonify({"error": "Unable to create booking"}), 500

    finally:
        connection.close()

@app.route("/bookings", methods=["GET"])
def list_bookings():
    connection = get_db_connection()

    bookings = connection.execute(
        """
        SELECT
            bookings.id,
            bookings.slot_id,
            bookings.patient_name,
            bookings.patient_email,
            bookings.status,
            bookings.created_at,
            slots.clinic_id,
            slots.starts_at,
            slots.ends_at
        FROM bookings
        JOIN slots ON bookings.slot_id = slots.id
        ORDER BY bookings.id DESC
        """
    ).fetchall()

    connection.close()

    return jsonify({
        "bookings": [dict(booking) for booking in bookings]
    }), 200

@app.route("/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    connection = get_db_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        booking = connection.execute(
            """
            SELECT id, slot_id, status
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,)
        ).fetchone()

        if booking is None:
            connection.rollback()
            return jsonify({"error": "Booking not found"}), 404

        if booking["status"] == "cancelled":
            connection.rollback()
            return jsonify({"error": "Booking is already cancelled"}), 409

        connection.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?",
            (booking_id,)
        )

        connection.execute(
            "UPDATE slots SET status = 'available' WHERE id = ?",
            (booking["slot_id"],)
        )

        connection.commit()

        return jsonify({
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "status": "cancelled",
            "slot_status": "available"
        }), 200

    except Exception:
        connection.rollback()
        app.logger.exception("Failed to cancel booking")
        return jsonify({"error": "Unable to cancel booking"}), 500

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
