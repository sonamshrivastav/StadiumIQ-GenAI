"""
StadiumIQ — FastAPI Backend
FIFA World Cup 2026 GenAI Stadium Command Center
"""

import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from schema import (
    ChatRequest, ChatResponse, CompanionRequest, IncidentRequest,
    TaskRequest, CarbonRequest, TravelTimeRequest
)
from data import STADIUMS, MATCHES, get_crowd_data
from tools import (
    find_nearest_facility, get_accessible_route, find_sensory_room,
    request_companion_assistance, get_transit_options, estimate_travel_time,
    find_parking, calculate_carbon_footprint, find_recycling_station,
    get_sustainability_score, report_incident, get_active_incidents,
    assign_staff_task, get_staff_overview
)
from unified_agent import run_chat_query

# ──────────────────────────────────────────────
# APP SETUP
# ──────────────────────────────────────────────

app = FastAPI(
    title="StadiumIQ API",
    description="GenAI-powered FIFA World Cup 2026 Stadium Command Center",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App initialization complete


# ──────────────────────────────────────────────
# CHAT ENDPOINT
# ──────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the StadiumIQ AI assistant using the optimized unified GenAI client."""
    session_id = request.session_id or "default-session"
    stadium_id = request.stadium_id or "metlife"
    language = request.language or "en"
    
    reply, agent_used = await run_chat_query(
        session_id=session_id,
        message=request.message,
        stadium_id=stadium_id,
        language=language
    )
    
    suggestions = _get_suggestions(request.message)
    
    return ChatResponse(
        reply=reply,
        agent_used=agent_used,
        stadium_id=stadium_id,
        suggestions=suggestions,
    )


def _get_suggestions(message: str) -> list[str]:
    """Generate contextual follow-up suggestions based on the user's message."""
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["food", "eat", "hungry", "restaurant"]):
        return ["Find nearest restroom", "Show match schedule", "How crowded is the food court?"]
    elif any(w in msg_lower for w in ["restroom", "bathroom", "toilet", "washroom"]):
        return ["Find nearest food court", "What's the crowd like?", "Accessible restrooms nearby"]
    elif any(w in msg_lower for w in ["crowd", "busy", "congested", "packed"]):
        return ["Best exit route", "Predict congestion in 30 min", "Find a quiet area"]
    elif any(w in msg_lower for w in ["exit", "leave", "gate"]):
        return ["Best exit right now", "How do I get to the parking lot?", "Transit options home"]
    elif any(w in msg_lower for w in ["wheelchair", "accessible", "disability", "ramp"]):
        return ["Find sensory room", "Request companion assistance", "Accessible restrooms"]
    elif any(w in msg_lower for w in ["transit", "bus", "train", "shuttle", "uber"]):
        return ["Find parking", "Carbon footprint of my trip", "Best exit for transit"]
    elif any(w in msg_lower for w in ["recycle", "green", "carbon", "eco", "sustain"]):
        return ["Find recycling station", "Stadium sustainability score", "Carbon footprint calculator"]
    elif any(w in msg_lower for w in ["incident", "report", "spill", "broken", "emergency"]):
        return ["View active incidents", "Staff overview", "Request maintenance"]
    else:
        return ["Find nearest restroom", "How crowded is it?", "Show match schedule", "Transit options"]


# ──────────────────────────────────────────────
# STADIUM DATA ENDPOINTS
# ──────────────────────────────────────────────

@app.get("/api/stadiums")
async def get_stadiums():
    """Get all 16 FIFA World Cup 2026 stadiums."""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "city": s["city"],
            "country": s["country"],
            "capacity": s["capacity"],
            "lat": s["lat"],
            "lng": s["lng"],
        }
        for s in STADIUMS.values()
    ]


@app.get("/api/stadiums/{stadium_id}")
async def get_stadium(stadium_id: str):
    """Get detailed info for a specific stadium."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}
    return stadium


@app.get("/api/stadiums/{stadium_id}/facilities")
async def get_facilities(stadium_id: str):
    """Get all facilities at a stadium."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}
    return stadium.get("facilities", {})


@app.get("/api/crowd/{stadium_id}")
async def get_crowd(stadium_id: str):
    """Get simulated real-time crowd density for a stadium."""
    return get_crowd_data(stadium_id)


@app.get("/api/matches")
async def get_matches(stadium_id: str = None):
    """Get the upcoming match schedule."""
    if stadium_id:
        return [m for m in MATCHES if m["stadium_id"] == stadium_id]
    return MATCHES


# ──────────────────────────────────────────────
# DETAILED DOMAIN ENDPOINTS FOR FRONTEND
# ──────────────────────────────────────────────

@app.get("/api/stadiums/{stadium_id}/facilities/{facility_type}")
async def api_find_nearest_facility(stadium_id: str, facility_type: str):
    """Find facilities of a given type in a stadium (e.g. food, restroom, medical)."""
    return find_nearest_facility(stadium_id, facility_type)


@app.get("/api/accessibility/route/{stadium_id}/{section}")
async def api_get_accessible_route(stadium_id: str, section: str):
    """Calculate wheelchair-accessible route to a specific section."""
    return get_accessible_route(stadium_id, section)


@app.get("/api/accessibility/sensory-room/{stadium_id}")
async def api_find_sensory_room(stadium_id: str):
    """Get sensory rooms and calm zones availability."""
    return find_sensory_room(stadium_id)


@app.post("/api/accessibility/companion")
async def api_request_companion(request: CompanionRequest):
    """Request a volunteer companion for navigation assistance."""
    return request_companion_assistance(request.stadium_id, request.current_location, request.assistance_type)


@app.get("/api/transit/{stadium_id}")
async def api_get_transit(stadium_id: str):
    """Get transit options and parking lot list for a stadium."""
    options = get_transit_options(stadium_id)
    parking = find_parking(stadium_id)
    return {"transit": options, "parking": parking}


@app.post("/api/transit/estimate")
async def api_estimate_travel(request: TravelTimeRequest):
    """Estimate travel time to a stadium from an origin by mode."""
    return estimate_travel_time(request.stadium_id, request.origin, request.mode)


@app.post("/api/sustainability/carbon")
async def api_calculate_carbon(request: CarbonRequest):
    """Calculate carbon footprint and comparison for a trip."""
    return calculate_carbon_footprint(request.transport_mode, request.distance_km)


@app.get("/api/sustainability/recycling/{stadium_id}")
async def api_find_recycling(stadium_id: str):
    """Get recycling stations and composting instructions."""
    return find_recycling_station(stadium_id)


@app.get("/api/sustainability/score/{stadium_id}")
async def api_get_sustainability_score(stadium_id: str):
    """Get sustainability rating and green initiatives."""
    return get_sustainability_score(stadium_id)


@app.get("/api/ops/incidents/{stadium_id}")
async def api_get_incidents(stadium_id: str):
    """Get active incidents logged in the stadium."""
    return get_active_incidents(stadium_id)


@app.post("/api/ops/incidents")
async def api_report_incident(request: IncidentRequest):
    """Report a new operational incident."""
    return report_incident(request.stadium_id, request.description, request.location)


@app.post("/api/ops/tasks")
async def api_assign_task(request: TaskRequest):
    """Assign an operational task to staff/volunteers."""
    return assign_staff_task(request.stadium_id, request.task_description, request.priority)


@app.get("/api/ops/staff/{stadium_id}")
async def api_get_staff(stadium_id: str):
    """Get staff deployment status and shift details."""
    return get_staff_overview(stadium_id)



# ──────────────────────────────────────────────
# WEBSOCKET — Live Updates
# ──────────────────────────────────────────────

connected_clients: list[WebSocket] = []


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket endpoint for live crowd and incident updates."""
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Send crowd update every 10 seconds
            data = get_crowd_data("metlife")  # Default stadium
            await websocket.send_json({"type": "crowd_update", "data": data})
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


# ──────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────

@app.get("/")
@app.get("/healthz")
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "StadiumIQ API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
