"""
StadiumIQ — Agent Tool Functions
These functions are callable by ADK agents to access stadium data,
crowd info, navigation, transit, sustainability metrics, and ops.
"""

import random
import math
from data import STADIUMS, MATCHES, get_crowd_data, report_new_incident, get_incidents


# ──────────────────────────────────────────────
# FAN ASSISTANT TOOLS
# ──────────────────────────────────────────────

def get_stadium_info(stadium_id: str) -> dict:
    """Get detailed information about a specific FIFA World Cup 2026 stadium including capacity, location, and available facilities."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": f"Stadium '{stadium_id}' not found. Available: {list(STADIUMS.keys())}"}
    return {
        "name": stadium["name"],
        "city": stadium["city"],
        "country": stadium["country"],
        "capacity": stadium["capacity"],
        "coordinates": {"lat": stadium["lat"], "lng": stadium["lng"]},
        "facility_types": list(stadium["facilities"].keys()),
    }


def find_nearest_facility(stadium_id: str, facility_type: str) -> dict:
    """Find the nearest facility of a given type in a stadium. Types: food, restroom, medical, exit, accessibility, recycling."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    type_map = {
        "food": "food_courts", "restroom": "restrooms", "restrooms": "restrooms",
        "medical": "medical", "exit": "exits", "exits": "exits",
        "accessibility": "accessibility", "accessible": "accessibility",
        "recycling": "recycling", "recycle": "recycling", "eco": "recycling",
        "bathroom": "restrooms", "toilet": "restrooms", "washroom": "restrooms",
        "first aid": "medical", "doctor": "medical", "nurse": "medical",
        "wheelchair": "accessibility", "elevator": "accessibility",
    }

    key = type_map.get(facility_type.lower(), facility_type.lower())
    facilities = stadium["facilities"].get(key, [])

    if not facilities:
        return {"error": f"No '{facility_type}' facilities found. Available types: {list(stadium['facilities'].keys())}"}

    # Simulate wait times and distance
    results = []
    for f in facilities:
        wait = random.randint(0, 8)
        dist = random.randint(20, 150)
        results.append({
            "name": f["name"],
            "section": f["section"],
            "distance_meters": dist,
            "estimated_walk_min": max(1, dist // 40),
            "current_wait_min": wait,
            "status": "available" if wait < 5 else "busy",
        })

    results.sort(key=lambda x: x["distance_meters"])
    return {"stadium": stadium["name"], "type": facility_type, "results": results}


def get_match_schedule(stadium_id: str = None) -> dict:
    """Get the upcoming FIFA World Cup 2026 match schedule, optionally filtered by stadium."""
    if stadium_id:
        matches = [m for m in MATCHES if m["stadium_id"] == stadium_id]
    else:
        matches = MATCHES

    if not matches:
        return {"message": "No upcoming matches found for this stadium."}

    result = []
    for m in matches:
        stadium = STADIUMS.get(m["stadium_id"], {})
        result.append({
            "match": f"{m['team1']} vs {m['team2']}",
            "group": f"Group {m['group']}",
            "date": m["date"],
            "time": m["time"],
            "stadium": stadium.get("name", "Unknown"),
            "city": stadium.get("city", "Unknown"),
            "status": m["status"],
        })
    return {"matches": result}


# ──────────────────────────────────────────────
# CROWD INTELLIGENCE TOOLS
# ──────────────────────────────────────────────

def check_crowd_density(stadium_id: str) -> dict:
    """Check real-time crowd density across all zones of a stadium. Returns occupancy percentages, wait times, and congestion alerts."""
    return get_crowd_data(stadium_id)


def suggest_best_exit(stadium_id: str) -> dict:
    """Suggest the best (least crowded) exit gate based on current crowd density at a stadium."""
    crowd = get_crowd_data(stadium_id)
    if "error" in crowd:
        return crowd

    gate_zones = [z for z in crowd["zones"] if "Gate" in z["zone"]]
    if not gate_zones:
        return {"error": "No gate data available"}

    best = min(gate_zones, key=lambda z: z["density_pct"])
    worst = max(gate_zones, key=lambda z: z["density_pct"])

    return {
        "recommended_exit": best["zone"],
        "recommended_density": f"{best['density_pct']}%",
        "recommended_wait": f"{best['wait_time_min']} min",
        "avoid_exit": worst["zone"],
        "avoid_density": f"{worst['density_pct']}%",
        "avoid_wait": f"{worst['wait_time_min']} min",
        "tip": f"Use {best['zone']} to save approximately {worst['wait_time_min'] - best['wait_time_min']} minutes compared to {worst['zone']}.",
    }


def predict_congestion(stadium_id: str, minutes_ahead: int = 30) -> dict:
    """Predict crowd congestion at a stadium for the next N minutes based on current trends."""
    crowd = get_crowd_data(stadium_id)
    if "error" in crowd:
        return crowd

    predictions = []
    for zone in crowd["zones"]:
        trend = random.choice(["increasing", "stable", "decreasing"])
        delta = random.randint(-10, 15)
        predicted = max(0, min(100, zone["density_pct"] + delta))
        predictions.append({
            "zone": zone["zone"],
            "current_pct": zone["density_pct"],
            "predicted_pct": predicted,
            "trend": trend,
            "recommendation": "Consider moving soon" if predicted > 80 else "Safe to stay",
        })

    return {
        "stadium": crowd["stadium_name"],
        "prediction_window": f"Next {minutes_ahead} minutes",
        "predictions": predictions,
    }


# ──────────────────────────────────────────────
# ACCESSIBILITY TOOLS
# ──────────────────────────────────────────────

def get_accessible_route(stadium_id: str, destination_section: str) -> dict:
    """Get wheelchair-accessible route to a specific section in the stadium, including elevators and ramps."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    access_facilities = stadium["facilities"].get("accessibility", [])

    route_steps = [
        f"Enter via {access_facilities[0]['name']} ({access_facilities[0]['section']})" if access_facilities else "Enter via main accessible entrance",
        "Proceed along the accessible concourse (flat surface, 2.5m wide)",
        f"Take Elevator to Level {random.choice(['1', '2', '3'])}",
        "Follow blue accessibility markers along corridor",
        f"Arrive at Section {destination_section} — wheelchair spaces on Row 1",
    ]

    return {
        "stadium": stadium["name"],
        "destination": f"Section {destination_section}",
        "route": route_steps,
        "estimated_time_min": random.randint(4, 10),
        "accessibility_features": [
            "Ramp access at entrance",
            "Elevator to all levels",
            "Wheelchair-designated spaces",
            "Companion seating adjacent",
            "Accessible restroom nearby",
        ],
        "tip": "Companion assistants are available — ask any volunteer in a blue vest for help.",
    }


def find_sensory_room(stadium_id: str) -> dict:
    """Find sensory/quiet rooms for neurodivergent fans or those who need a calm space."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    return {
        "stadium": stadium["name"],
        "sensory_rooms": [
            {
                "name": "Quiet Zone A",
                "location": "Section 200, Level 2",
                "features": ["Low lighting", "Sound dampening", "Fidget tools", "Comfortable seating", "Live match feed on screen"],
                "capacity": 12,
                "currently_available": random.randint(2, 8),
            }
        ],
        "tip": "Sensory rooms are open throughout the match. No reservation needed — first come, first served.",
    }


def request_companion_assistance(stadium_id: str, current_location: str, assistance_type: str) -> dict:
    """Request a volunteer companion to assist with navigation, wheelchair pushing, or language translation."""
    return {
        "status": "confirmed",
        "request_id": f"ASSIST-{random.randint(1000, 9999)}",
        "eta_minutes": random.randint(2, 6),
        "volunteer_name": random.choice(["Maria", "James", "Aiko", "Carlos", "Priya"]),
        "meeting_point": current_location,
        "assistance_type": assistance_type,
        "message": f"A volunteer will meet you at {current_location} in approximately {random.randint(2, 6)} minutes.",
    }


# ──────────────────────────────────────────────
# TRANSIT & TRANSPORTATION TOOLS
# ──────────────────────────────────────────────

def get_transit_options(stadium_id: str) -> dict:
    """Get all transportation options for getting to/from a FIFA World Cup 2026 stadium."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    return {
        "stadium": stadium["name"],
        "city": stadium["city"],
        "options": stadium.get("transit", {}),
        "recommendation": "🌿 Taking public transit reduces your carbon footprint by up to 80% compared to driving alone.",
    }


def estimate_travel_time(stadium_id: str, origin: str, mode: str = "transit") -> dict:
    """Estimate travel time to a stadium from a given origin point by different transport modes."""
    base_times = {"transit": 40, "rideshare": 25, "shuttle": 50, "walking": 90, "driving": 20}
    base = base_times.get(mode, 30)
    variation = random.randint(-10, 15)

    return {
        "origin": origin,
        "destination": STADIUMS.get(stadium_id, {}).get("name", "Unknown Stadium"),
        "mode": mode,
        "estimated_minutes": max(10, base + variation),
        "traffic_status": random.choice(["light", "moderate", "heavy"]),
        "tip": "Allow extra time on match days. Gates open 3 hours before kickoff.",
    }


def find_parking(stadium_id: str) -> dict:
    """Find available parking near a FIFA World Cup 2026 stadium with pricing and availability."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    transit = stadium.get("transit", {})
    parking_info = transit.get("parking", "Parking info not available")

    lots = [
        {"lot": "Lot A (Closest)", "distance_walk_min": 5, "availability": f"{random.randint(10, 40)}%", "price": "$60"},
        {"lot": "Lot C (Standard)", "distance_walk_min": 10, "availability": f"{random.randint(30, 70)}%", "price": "$45"},
        {"lot": "Lot E (Economy)", "distance_walk_min": 18, "availability": f"{random.randint(50, 90)}%", "price": "$30"},
    ]

    return {
        "stadium": stadium["name"],
        "general_info": parking_info,
        "lots": lots,
        "eco_tip": "🌿 Consider carpooling or using the free FIFA shuttle to reduce emissions and avoid parking hassle!",
    }


# ──────────────────────────────────────────────
# SUSTAINABILITY TOOLS
# ──────────────────────────────────────────────

def calculate_carbon_footprint(transport_mode: str, distance_km: float = 20) -> dict:
    """Calculate estimated carbon footprint for traveling to the stadium based on transport mode and distance."""
    emissions_per_km = {
        "car_solo": 0.21,
        "car_carpool": 0.08,
        "rideshare": 0.12,
        "bus": 0.05,
        "train": 0.03,
        "subway": 0.03,
        "shuttle": 0.04,
        "bicycle": 0.0,
        "walking": 0.0,
    }

    factor = emissions_per_km.get(transport_mode.lower(), 0.15)
    total_kg = round(factor * distance_km, 2)

    best_mode = min(emissions_per_km, key=emissions_per_km.get)
    savings = round((0.21 * distance_km) - total_kg, 2)

    return {
        "transport_mode": transport_mode,
        "distance_km": distance_km,
        "co2_kg": total_kg,
        "comparison_to_car": f"{'Saves' if savings > 0 else 'Adds'} {abs(savings)} kg CO₂ vs driving alone",
        "eco_rating": "🌱 Excellent" if total_kg < 1 else "🌿 Good" if total_kg < 2 else "🍂 Fair" if total_kg < 4 else "🔴 High",
        "tip": f"Best option: {best_mode} ({emissions_per_km[best_mode]} kg/km). Every small choice adds up across 3.5 million fans!",
    }


def find_recycling_station(stadium_id: str) -> dict:
    """Find recycling, composting, and waste reduction stations at a stadium."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    recycling = stadium["facilities"].get("recycling", [])

    stations = []
    for r in recycling:
        stations.append({
            "name": r["name"],
            "section": r["section"],
            "accepts": ["Plastic bottles", "Aluminum cans", "Paper", "Food waste (compost)"],
            "distance_meters": random.randint(15, 80),
        })

    return {
        "stadium": stadium["name"],
        "stations": stations,
        "tips": [
            "♻️ Separate liquids before recycling cups",
            "🍂 Food scraps go in the BROWN compost bin",
            "💧 Refill your water bottle at free stations to avoid plastic waste",
            "🎟️ Keep your digital ticket — no paper waste!",
        ],
    }


def get_sustainability_score(stadium_id: str) -> dict:
    """Get the sustainability score and eco-initiatives for a stadium during the World Cup."""
    stadium = STADIUMS.get(stadium_id)
    if not stadium:
        return {"error": "Stadium not found"}

    return {
        "stadium": stadium["name"],
        "sustainability_score": f"{random.randint(72, 95)}/100",
        "initiatives": [
            "100% renewable energy for match-day operations",
            "Zero single-use plastic policy",
            "Rainwater harvesting for irrigation",
            "Carbon offset program for all ticket holders",
            "Local food sourcing within 100-mile radius",
            "Post-event recycling target: 90%",
        ],
        "fan_impact": "Your attendance today contributes to FIFA's goal of a carbon-neutral World Cup 2026!",
    }


# ──────────────────────────────────────────────
# OPERATIONS & STAFF TOOLS
# ──────────────────────────────────────────────

def report_incident(stadium_id: str, description: str, location: str) -> dict:
    """Report an operational incident at a stadium (spills, equipment issues, safety concerns, medical emergencies)."""
    return report_new_incident(stadium_id, description, location)


def get_active_incidents(stadium_id: str) -> dict:
    """Get all active incidents reported at a stadium."""
    incidents = get_incidents(stadium_id)
    return {
        "stadium": STADIUMS.get(stadium_id, {}).get("name", "Unknown"),
        "total_incidents": len(incidents),
        "incidents": incidents,
    }


def assign_staff_task(stadium_id: str, task_description: str, priority: str = "medium") -> dict:
    """Assign a task to the nearest available staff member or volunteer at a stadium."""
    return {
        "task_id": f"TASK-{random.randint(5000, 9999)}",
        "stadium": STADIUMS.get(stadium_id, {}).get("name", "Unknown"),
        "description": task_description,
        "priority": priority,
        "assigned_to": random.choice(["Volunteer Team A", "Security Unit 2", "Maintenance Crew C", "Guest Services"]),
        "status": "assigned",
        "eta_minutes": random.randint(3, 12),
    }


def get_staff_overview(stadium_id: str) -> dict:
    """Get an overview of staff and volunteer deployment status at a stadium."""
    return {
        "stadium": STADIUMS.get(stadium_id, {}).get("name", "Unknown"),
        "staff_deployed": {
            "security": {"total": 120, "active": random.randint(100, 118), "on_break": random.randint(2, 20)},
            "volunteers": {"total": 200, "active": random.randint(160, 195), "on_break": random.randint(5, 40)},
            "medical": {"total": 30, "active": random.randint(25, 29), "on_break": random.randint(1, 5)},
            "maintenance": {"total": 40, "active": random.randint(30, 38), "on_break": random.randint(2, 10)},
            "food_service": {"total": 80, "active": random.randint(65, 78), "on_break": random.randint(2, 15)},
        },
        "shift_change_in": f"{random.randint(1, 4)} hours",
        "morale": random.choice(["Excellent ⭐", "Good 👍", "Fair 👌"]),
    }


def get_stadium_weather(stadium_id: str) -> dict:
    """Get detailed weather information for a specific FIFA World Cup 2026 stadium, including current conditions (temp, humidity, rain probability) and forecast."""
    from weather_football_service import get_weather_data
    return get_weather_data(stadium_id)


def get_stadium_match_data(stadium_id: str) -> dict:
    """Get today's football match data (score, kickoff time, status, goals, cards, teams, venue) for a specific FIFA World Cup 2026 stadium."""
    from weather_football_service import get_football_data
    return get_football_data(stadium_id)

