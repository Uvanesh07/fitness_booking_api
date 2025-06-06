from fastapi import FastAPI, HTTPException, Query
from pydantic import EmailStr
from app.models.schemas import FitnessClass, BookingRequest, BookingResponse
from typing import List
from datetime import datetime
import logging
import pytz
from app.utils import read_json, write_json

app = FastAPI()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fitness_booking")

# Constants
CLASSES_FILE = "app/data/classes.json"
BOOKINGS_FILE = "app/data/bookings.json"
IST = pytz.timezone("Asia/Kolkata")

@app.get("/classes", response_model=List[FitnessClass])
def get_classes(timezone: str = Query("Asia/Kolkata")):
    try:
        user_tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    now_ist = datetime.now(IST)
    classes = read_json(CLASSES_FILE)

    upcoming = [
        {
            **cls,
            "datetime": datetime.fromisoformat(cls["datetime"])
            .astimezone(IST)
            .astimezone(user_tz)
            .isoformat()
        }
        for cls in classes
        if datetime.fromisoformat(cls["datetime"]).astimezone(IST) > now_ist
    ]
    return upcoming


@app.post("/book", response_model=BookingResponse)
def book_class(booking: BookingRequest):
    if not booking.client_name.strip():
        raise HTTPException(status_code=422, detail="Client name cannot be empty")

    classes = read_json(CLASSES_FILE)
    bookings = read_json(BOOKINGS_FILE)

    cls = next((c for c in classes if c["id"] == booking.class_id), None)
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if cls["available_slots"] <= 0:
        raise HTTPException(status_code=400, detail="No available slots")

    email = booking.client_email.lower()
    if any(b for b in bookings if b["class_id"] == booking.class_id and b["client_email"].lower() == email):
        raise HTTPException(status_code=409, detail="You have already booked this class")

    cls["available_slots"] -= 1
    updated_classes = [c if c["id"] != cls["id"] else cls for c in classes]
    write_json(CLASSES_FILE, updated_classes)

    booking_record = {
        "class_id": cls["id"],
        "class_name": cls["name"],
        "datetime": cls["datetime"],
        "client_name": booking.client_name,
        "client_email": booking.client_email,
    }
    bookings.append(booking_record)
    write_json(BOOKINGS_FILE, bookings)

    logger.info(f"Booking successful: {booking_record}")
    return booking_record


@app.get("/bookings", response_model=List[BookingResponse])
def get_bookings(email: EmailStr):
    email = email.lower()
    bookings = read_json(BOOKINGS_FILE)
    return [b for b in bookings if b["client_email"].lower() == email]
