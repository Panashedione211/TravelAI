from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth_utils import get_current_user
from foundry import chat_update_trip, generate_itinerary 

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
        import traceback
        traceback.print_exc()
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


# POST /api/trips/{trip_id}/chat
# sends current stops + user message to Foundry, replaces all stops with the updated list
@router.post("/{trip_id}/chat", response_model=schemas.GenerateResponse)
def chat(
    trip_id: int,
    body: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = db.query(models.Trip).filter(
        models.Trip.id == trip_id,
        models.Trip.user_id == current_user.id,
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    stops = db.query(models.ItineraryStop).filter(
        models.ItineraryStop.trip_id == trip_id
    ).order_by(models.ItineraryStop.day_number, models.ItineraryStop.stop_number).all()

    stops_data = [
        {"day_number": s.day_number, "stop_number": s.stop_number,
         "name": s.name, "description": s.description, "lat": s.lat, "lng": s.lng,
         "estimated_cost": s.estimated_cost or 0}
        for s in stops
    ]

    try:
        updated_stops_data = chat_update_trip(trip, stops_data, body.message)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Chat failed: {str(e)}")

    # delete all existing stops and replace with the updated list
    db.query(models.ItineraryStop).filter(
        models.ItineraryStop.trip_id == trip_id
    ).delete()
    db.commit()

    saved_stops = []
    # save each updated stop to the database
    for stop in updated_stops_data:
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

    db.commit()
    for s in saved_stops:
        db.refresh(s)

    return schemas.GenerateResponse(
        trip_id=trip_id,
        status="updated",
        stops=saved_stops,
    )
