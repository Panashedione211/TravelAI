# TravelAI Models Relationship Diagram

This diagram shows how the database models in `Backend/models.py` are connected.

## Tables and relationships

```text
+-----------------+        1        +-----------------+        1        +----------------------+
|      users      |----------------<|      trips      |----------------<|   itinerary_stops    |
+-----------------+   user_id fk    +-----------------+   trip_id fk    +----------------------+
| id (PK)         |                | id (PK)         |                | id (PK)              |
| username        |                | user_id         |                | trip_id              |
| email           |                | destination     |                | day_number           |
| password_hash   |                | days            |                | stop_number          |
| created_at      |                | budget          |                | name                 |
|                 |                | travel_style    |                | description          |
|                 |                | pace            |                | lat                  |
|                 |                | group_type      |                | lng                  |
|                 |                | status          |                | estimated_cost       |
|                 |                | created_at      |                | created_at           |
+-----------------+                +-----------------+                +----------------------+

User 1 — N Trip
Trip 1 — N ItineraryStop
```

## Relationship details

- `User.trips` is a one-to-many relationship from `User` to `Trip`.
  - One user can have many trips.
- `Trip.user` is the reverse relationship from `Trip` to `User`.
  - Each trip belongs to one user.
- `Trip.stops` is a one-to-many relationship from `Trip` to `ItineraryStop`.
  - One trip can have many stops.
- `ItineraryStop.trip` is the reverse relationship from `ItineraryStop` to `Trip`.
  - Each stop belongs to one trip.

## How it works in `models.py`

- `ForeignKey("users.id")` on `Trip.user_id` makes the database connect each trip to a user.
- `relationship("User", back_populates="trips")` lets Python use `trip.user`.
- `ForeignKey("trips.id")` on `ItineraryStop.trip_id` makes the database connect each stop to a trip.
- `relationship("Trip", back_populates="stops")` lets Python use `stop.trip`.

## Plain language

- A user is the owner of trips.
- A trip belongs to a user.
- A trip contains stops.
- A stop belongs to a trip.
