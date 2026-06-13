from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

"""this file defenes our schemas and tells fastapi how to return and send data from the api endpoints, 
it also does validation on incoming data to make sure it has the correct format and types. 
It uses pydantic models to define the structure of the data for users, trips, and itinerary stops.
"""

# without it fastapi might return to little or too much data, in the wrong fromat which would cause bugs.
# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ── Trips ─────────────────────────────────────────────────────────────────────

class TripCreate(BaseModel):
    destination: str
    days: int
    budget: str
    travel_style: str
    pace: str
    group_type: str


class TripOut(BaseModel):
    id: int
    destination: str
    days: int
    budget: str
    travel_style: str
    pace: str
    group_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Itinerary Stops ───────────────────────────────────────────────────────────

class StopOut(BaseModel):
    id: int
    trip_id: int
    day_number: int
    stop_number: int
    name: str
    description: Optional[str]
    lat: Optional[float]
    lng: Optional[float]
    estimated_cost: Optional[float]

    class Config:
        from_attributes = True
