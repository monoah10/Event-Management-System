from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from backend.database import SessionLocal
from backend.models import Event, User, event_attendees
from backend.schemas import EventCreate, EventResponse, EventUpdate
from backend.auth import get_current_user, is_admin
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/events", tags=["Events Management"])


@router.post("/", summary="Create a new event", response_model=EventResponse)
async def create_event(event: EventCreate, user: User = Depends(get_current_user)):
    """
    Allows an **organizer** or **admin** to create a new event.
    The organizer_id is automatically set to the current user.
    """
    if user.role not in ["organizer", "admin"]:
        raise HTTPException(status_code=403, detail="Only organizers and Admin can create events")

    db = SessionLocal()
    new_event = Event(**event.dict(), organizer_id=user.id)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.get("/", summary="List all events", response_model=list[EventResponse])
async def list_events(
        location: Optional[str] = Query(None, description="Filter by location (partial match allowed)"),
        available_only: bool = Query(False, description="Show only events that are not full"),
        limit: int = Query(10, description="Number of events to return"),
        offset: int = Query(0, description="Number of events to skip")
):
    """
    Retrieves a list of events with optional filtering by location, availability,
    pagination using limit & offset.
    """
    db = SessionLocal()
    query = db.query(Event)

    if location:
        query = query.filter(Event.location.ilike(f"%{location}%"))

    all_events = query.all()
    if available_only:
        filtered = [event for event in all_events if len(event.attendees) < event.max_attendees]
    else:
        filtered = all_events
    paginated = filtered[offset:offset + limit]
    return paginated


@router.get("/{event_id}", summary="List event By ID ", response_model=EventResponse)
async def list_event_by_id(event_id:int, current_user: User = Depends(get_current_user)):
    """
    Retrieves a list of events with optional filtering by location, availability,
    pagination using limit & offset.
    """
    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/{event_id}/join", summary="Join an event")
def join_event(event_id: int, current_user: User = Depends(get_current_user)):
    """
    Allows a logged-in user to join an event by its ID.
    Validates against max attendee limit and prevents rejoining.
    """
    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user_in_session = db.merge(current_user)
    if current_user in event.attendees:
        raise HTTPException(status_code=400, detail="You have already joined this event")

    if len(event.attendees) >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is full.")

    event.attendees.append(user_in_session)
    db.commit()
    return {"message": "Successfully joined the event"}


@router.delete("/{event_id}/delete", summary="Delete an event (Admin/Organizer only)")
def delete_event(event_id: int, current_user: User = Depends(get_current_user)):
    """
    Allows an **admin** or **organizer** to delete an event by ID.
    """
    db = SessionLocal()
    if current_user.role not in ["admin", "organizer"]:
        raise HTTPException(status_code=403, detail="Only admins can delete events")

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.query(event_attendees).filter(event_attendees.c.event_id == event_id).delete(synchronize_session=False)
    db.delete(event)
    db.commit()
    return {"message": "Event deleted successfully"}


@router.put("/{event_id}/update", summary="Update an event (Admin/Organizer only)")
def update_event(event_id: int, event_data: EventUpdate, user: User = Depends(get_current_user)):
    """
    Allows an **organizer** or **admin** to update event details.
    Supports partial updates using PATCH-like behavior.
    """
    if user.role not in ["organizer", "admin"]:
        raise HTTPException(status_code=403, detail="Only organizers and Admin can update events")

    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return {"message": "Event updated successfully", "event": event}


@router.delete("/{event_id}/attendees/{user_id}",  summary="Remove attendees from an event (Admin/Organizer only)")
async def remove_attendee_from_event(event_id: int, user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "organizer"]:
        raise HTTPException(status_code=403, detail="Only admins can delete events")

    db = SessionLocal()
    event = db.query(Event).options(joinedload(Event.attendees)).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user not in event.attendees:
        raise HTTPException(status_code=404, detail="User not found in attendees")

    event.attendees.remove(user)
    db.commit()
    return {"detail": f"User {user.username} removed from event"}