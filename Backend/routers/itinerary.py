from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth_utils import get_current_user
from foundry import generate_itinerary

router = APIRouter(prefix="/api/trips", tags=["itinerary"])


# POST /api/trips/{trip_id}/generate
# calls Foundry AI, saves stops to DB, updates trip status to "generated"
@router.post("/{trip_id}/generate", response_model=schemas.GenerateResponse)
def generate(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # make sure the trip exists and belongs to this user
    trip = db.query(models.Trip).filter(
        models.Trip.id == trip_id,
        models.Trip.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # delete any existing stops so we can regenerate cleanly
    db.query(models.ItineraryStop).filter(
        models.ItineraryStop.trip_id == trip_id
    ).delete()
    db.commit()

    # call Foundry (or mock) to get the itinerary
    try:
        stops_data = generate_itinerary(trip)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")

    # save each stop to the database
    saved_stops = []
    for stop in stops_data:
        db_stop = models.ItineraryStop(
            trip_id=trip_id,
            day_number=stop.get("day_number", 1),
            stop_number=stop.get("stop_number", 1),
            name=stop.get("name", "Unknown"),
            description=stop.get("description", ""),
            lat=stop.get("lat"),
            lng=stop.get("lng"),
            estimated_cost=stop.get("estimated_cost", 0.0),
        )
        db.add(db_stop)
        saved_stops.append(db_stop)

    # mark the trip as generated
    trip.status = "generated"
    db.commit()

    for s in saved_stops:
        db.refresh(s)

    return schemas.GenerateResponse(
        trip_id=trip_id,
        status="generated",
        stops=saved_stops,
    )
