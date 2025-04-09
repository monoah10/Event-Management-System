from pydantic import BaseModel, model_validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum
from typing import List


class UserRole(str, Enum):
    admin = "admin"
    organizer = "organizer"
    attendee = "attendee"


class LoginRequest(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "organizer", "attendee"]

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True
        orm_mode = True


class EventCreate(BaseModel):
    title: str
    description: str
    location: str
    date: datetime
    max_attendees: int

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    location: str
    date: datetime
    max_attendees: int
    attendees: List[UserResponse]
    available_space: Optional[int] = None

    class Config:
        from_attributes = True
        orm_mode = True

    @model_validator(mode="after")
    def calculate_available(self) -> "EventResponse":
        self.available_space = self.max_attendees - len(self.attendees or [])
        return self

class EventUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    max_attendees: Optional[int] = None