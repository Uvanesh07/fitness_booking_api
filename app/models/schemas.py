from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

class FitnessClass(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    datetime: datetime
    instructor: str = Field(..., min_length=1)
    available_slots: int = Field(..., ge=0)

    @validator('datetime')
    def ensure_datetime_in_ist(cls, value):
        if value.tzinfo is None:
            value = IST.localize(value)
        else:
            value = value.astimezone(IST)
        return value

class BookingRequest(BaseModel):
    class_id: int
    client_name: str = Field(..., min_length=1)
    client_email: EmailStr

class BookingResponse(BaseModel):
    class_id: int
    class_name: str
    datetime: datetime
    client_name: str
    client_email: EmailStr
