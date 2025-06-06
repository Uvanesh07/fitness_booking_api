from fastapi.testclient import TestClient
from app.main import app
import json
import os

client = TestClient(app)

# File paths
CLASSES_FILE = "app/data/classes.json"
BOOKINGS_FILE = "app/data/bookings.json"

# Test data
TEST_CLASS = {
    "id": 1,
    "name": "Yoga",
    "datetime": "2030-06-30T10:00:00+05:30",
    "available_slots": 5,
    "instructor": "Jane Doe"
}


TEST_BOOKING = {
    "class_id": 1,
    "client_name": "Test User",
    "client_email": "test@example.com"
}


def setup_module(module):
    """Reset JSON files before each test module run"""
    os.makedirs(os.path.dirname(CLASSES_FILE), exist_ok=True)
    with open(CLASSES_FILE, "w") as f:
        json.dump([TEST_CLASS], f)

    with open(BOOKINGS_FILE, "w") as f:
        json.dump([], f)


def test_get_classes_success():
    response = client.get("/classes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(c["id"] == TEST_CLASS["id"] for c in data)


def test_get_classes_invalid_timezone():
    response = client.get("/classes?timezone=Invalid/Zone")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid timezone"


def test_book_class_success():
    response = client.post("/book", json=TEST_BOOKING)
    assert response.status_code == 200
    data = response.json()
    assert data["client_email"] == TEST_BOOKING["client_email"]
    assert data["class_id"] == TEST_BOOKING["class_id"]


def test_book_class_already_booked():
    # Book once
    client.post("/book", json=TEST_BOOKING)

    # Book again with the same user and class
    response = client.post("/book", json=TEST_BOOKING)
    assert response.status_code == 409


def test_book_class_not_found():
    booking = TEST_BOOKING.copy()
    booking["class_id"] = 9999  # an int not in your classes.json
    response = client.post("/book", json=booking)
    assert response.status_code == 404
    assert response.json()["detail"] == "Class not found"


def test_book_class_no_slots():
    # Update class to have 0 slots
    with open(CLASSES_FILE, "w") as f:
        json.dump([{**TEST_CLASS, "available_slots": 0}], f)

    booking = {
        "class_id": TEST_CLASS["id"],
        "client_name": "Another User",
        "client_email": "another@example.com"
    }
    response = client.post("/book", json=booking)
    assert response.status_code == 400
    assert response.json()["detail"] == "No available slots"

    # Restore original class
    with open(CLASSES_FILE, "w") as f:
        json.dump([TEST_CLASS], f)


def test_book_class_empty_name():
    booking = {
        "class_id": TEST_CLASS["id"],
        "client_name": "   ",
        "client_email": "new@example.com"
    }
    response = client.post("/book", json=booking)
    assert response.status_code == 422
    assert response.json()["detail"] == "Client name cannot be empty"


def test_get_bookings_success():
    # Ensure the booking exists
    client.post("/book", json=TEST_BOOKING)

    response = client.get(f"/bookings?email={TEST_BOOKING['client_email']}")
    assert response.status_code == 200
    bookings = response.json()
    assert any(b["client_email"] == TEST_BOOKING["client_email"] for b in bookings)


def test_get_bookings_no_results():
    response = client.get("/bookings?email=notbooked@example.com")
    assert response.status_code == 200
    assert response.json() == []
