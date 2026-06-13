# is a python library for working with databases in python, we can interact with it using classes oop.
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# SQLAlchemy models for users, trips, and itinerary, knows the class is a database model
Base = declarative_base()

# table for users,
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="user")

# table for trips, each trip belongs to a user and has multiple itinerary stops
class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    budget = Column(String)           # "budget" | "mid-range" | "luxury"
    travel_style = Column(String)     # "hiking" | "food" | "city" | etc.
    pace = Column(String)             # "relaxed" | "balanced" | "packed"
    group_type = Column(String)       # "solo" | "couple" | "friends" | "family"
    status = Column(String, default="pending")  # "pending" | "generated"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")
    stops = relationship("ItineraryStop", back_populates="trip", cascade="all, delete") # to make sure all stops get deleted when a trip is deleted

# table for itinerary stops, each stop belongs to a trip
class ItineraryStop(Base):
    __tablename__ = "itinerary_stops"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    stop_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    estimated_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="stops")
