from sqlalchemy.orm import relationship
from backend.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
import datetime


event_attendees = Table(
    "event_attendees",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="attendee")
    organized_events = relationship("Event", back_populates="organizer")
    joined_events = relationship("Event", secondary=event_attendees, back_populates="attendees")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(String(500))
    location = Column(String(255))
    date = Column(DateTime)
    max_attendees = Column(Integer)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    organizer = relationship("User", back_populates="organized_events")
    attendees = relationship("User", secondary=event_attendees, back_populates="joined_events", cascade="all, delete",)


class RateLimit(Base):
    __tablename__ = "rate_limits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    ip_address = Column(String(80), nullable=True)
    count = Column(Integer, default=1)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
