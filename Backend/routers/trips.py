from fastapi import APIRouter, Depends, HTTPException  # APIRouter groups trip routes, Depends injects helpers, HTTPException sends errors
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas
from auth_utils import get_current_user

router = APIRouter(prefix="/api/trips", tags=["trips"])

# creates a trip for the current user, get data from questionnaire form saves it to the db and returns the created trip data.
@router.post("/", response_model=schemas.TripOut, status_code=201)
def create_trip(
    body: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = models.Trip(user_id=current_user.id, **body.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

# lists all trips for the current user, it queries the database for trips that belong to the authenticated user and returns them as a list.
# this is on the side of the page where the user can see all their trips and click on them to view details or delete them.
@router.get("/", response_model=List[schemas.TripOut])
def list_trips(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Trip).filter(models.Trip.user_id == current_user.id).all()

# gets a specific trip by ID, it checks if the trip belongs to the authenticated user and returns the trip data if found, otherwise it raises a 404 error.
# just gets 1 trip, this is used when the user clicks on a trip in the list to view its details.
@router.get("/{trip_id}", response_model=schemas.TripOut)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = db.query(models.Trip).filter(
        models.Trip.id == trip_id,
        models.Trip.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

# deletes a trip by ID, it checks if the trip belongs to the authenticated user and deletes it from the database if found, otherwise it raises a 404 error.
# this is used when the user clicks the delete button on a trip in the list, it removes the trip from the database and it will no longer show up in the list of trips.
@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = db.query(models.Trip).filter(
        models.Trip.id == trip_id,
        models.Trip.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()

# lists all stops for a specific trip, it checks if the trip belongs to the authenticated user and returns the list of stops if found, otherwise it raises a 404 error.
""" this is used on the trip details page to show all the stops that were generated for that trip 
when the user clicks on a trip in the list, it shows the details of that trip including the list of stops that were generated for it."""
@router.get("/{trip_id}/stops", response_model=List[schemas.StopOut])
def get_stops(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = db.query(models.Trip).filter(
        models.Trip.id == trip_id,
        models.Trip.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip.stops
