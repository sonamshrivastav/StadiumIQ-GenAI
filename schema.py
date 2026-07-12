"""
StadiumIQ — Pydantic Models for API Request/Response
Includes input validation constraints, field descriptions, and
type safety for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


# ──────────────────────────────────────────────
# SUPPORTED LANGUAGES
# ──────────────────────────────────────────────

SUPPORTED_LANGUAGES = Literal["en", "es", "fr", "pt", "de", "ar", "zh", "ja", "ko", "hi", "ru"]


# ──────────────────────────────────────────────
# CHAT MODELS
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request model for the AI chat endpoint."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question or message to the AI assistant."
    )
    stadium_id: Optional[str] = Field(
        default="metlife",
        max_length=50,
        description="ID of the active stadium context."
    )
    language: Optional[SUPPORTED_LANGUAGES] = Field(
        default="en",
        description="ISO language code for the response language."
    )
    session_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Unique session ID for conversation history tracking."
    )


class ChatResponse(BaseModel):
    """Response model for the AI chat endpoint."""
    reply: str = Field(description="The AI assistant's response text.")
    agent_used: Optional[str] = Field(default=None, description="Which AI persona handled the query.")
    stadium_id: Optional[str] = Field(default=None, description="The stadium context used for the response.")
    suggestions: Optional[list[str]] = Field(default=None, description="Contextual follow-up suggestion chips.")


# ──────────────────────────────────────────────
# STADIUM MODELS
# ──────────────────────────────────────────────

class StadiumResponse(BaseModel):
    """Response model for stadium information."""
    id: str = Field(description="Unique stadium identifier.")
    name: str = Field(description="Full stadium name.")
    city: str = Field(description="City where the stadium is located.")
    country: str = Field(description="Country where the stadium is located.")
    capacity: int = Field(description="Maximum seating capacity.")
    lat: float = Field(description="Latitude coordinate.")
    lng: float = Field(description="Longitude coordinate.")


# ──────────────────────────────────────────────
# CROWD MODELS
# ──────────────────────────────────────────────

class CrowdZone(BaseModel):
    """Model for a single crowd density zone."""
    zone: str = Field(description="Name of the stadium zone.")
    density_pct: int = Field(description="Current crowd density percentage.")
    people_count: int = Field(description="Estimated number of people in the zone.")
    status: str = Field(description="Zone status indicator (low/moderate/high/critical).")
    wait_time_min: int = Field(description="Estimated wait time in minutes.")


class CrowdResponse(BaseModel):
    """Response model for real-time crowd monitoring."""
    stadium_id: str = Field(description="Stadium identifier.")
    stadium_name: str = Field(description="Full stadium name.")
    total_capacity: int = Field(description="Maximum stadium capacity.")
    total_inside: int = Field(description="Current number of people inside.")
    occupancy_pct: float = Field(description="Current occupancy percentage.")
    zones: list[CrowdZone] = Field(description="Per-zone crowd density data.")
    timestamp: str = Field(description="ISO timestamp of the data snapshot.")
    alerts: list[dict] = Field(description="Active crowd alerts.")


# ──────────────────────────────────────────────
# ACCESSIBILITY MODELS
# ──────────────────────────────────────────────

class CompanionRequest(BaseModel):
    """Request model for volunteer companion assistance."""
    stadium_id: str = Field(
        ...,
        max_length=50,
        description="Stadium where assistance is needed."
    )
    current_location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Current location of the person requesting help."
    )
    assistance_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of assistance needed (e.g., wheelchair, visual, hearing)."
    )


# ──────────────────────────────────────────────
# OPERATIONS MODELS
# ──────────────────────────────────────────────

class IncidentRequest(BaseModel):
    """Request model for reporting operational incidents."""
    stadium_id: str = Field(
        ...,
        max_length=50,
        description="Stadium where the incident occurred."
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the incident."
    )
    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Physical location of the incident within the stadium."
    )


class TaskRequest(BaseModel):
    """Request model for assigning operational tasks."""
    stadium_id: str = Field(
        ...,
        max_length=50,
        description="Stadium for the task assignment."
    )
    task_description: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Description of the task to be assigned."
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority level (low, medium, high, critical)."
    )


# ──────────────────────────────────────────────
# SUSTAINABILITY MODELS
# ──────────────────────────────────────────────

class CarbonRequest(BaseModel):
    """Request model for carbon footprint calculation."""
    transport_mode: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mode of transport (car, bus, train, bicycle, walk)."
    )
    distance_km: float = Field(
        default=20.0,
        ge=0.0,
        le=1000.0,
        description="Distance traveled in kilometers."
    )


# ──────────────────────────────────────────────
# TRANSIT MODELS
# ──────────────────────────────────────────────

class TravelTimeRequest(BaseModel):
    """Request model for travel time estimation."""
    stadium_id: str = Field(
        ...,
        max_length=50,
        description="Destination stadium identifier."
    )
    origin: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Starting location for travel time calculation."
    )
    mode: Optional[str] = Field(
        default="transit",
        max_length=30,
        description="Travel mode (transit, driving, walking, cycling)."
    )
