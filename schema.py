"""
StadiumIQ — Pydantic Models for API Request/Response
"""

from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    stadium_id: Optional[str] = "metlife"
    language: Optional[str] = "en"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    agent_used: Optional[str] = None
    stadium_id: Optional[str] = None
    suggestions: Optional[list[str]] = None


class StadiumResponse(BaseModel):
    id: str
    name: str
    city: str
    country: str
    capacity: int
    lat: float
    lng: float


class CrowdZone(BaseModel):
    zone: str
    density_pct: int
    people_count: int
    status: str
    wait_time_min: int


class CrowdResponse(BaseModel):
    stadium_id: str
    stadium_name: str
    total_capacity: int
    total_inside: int
    occupancy_pct: float
    zones: list[CrowdZone]
    timestamp: str
    alerts: list[dict]


class CompanionRequest(BaseModel):
    stadium_id: str
    current_location: str
    assistance_type: str


class IncidentRequest(BaseModel):
    stadium_id: str
    description: str
    location: str


class TaskRequest(BaseModel):
    stadium_id: str
    task_description: str
    priority: Optional[str] = "medium"


class CarbonRequest(BaseModel):
    transport_mode: str
    distance_km: float = 20.0


class TravelTimeRequest(BaseModel):
    stadium_id: str
    origin: str
    mode: Optional[str] = "transit"

